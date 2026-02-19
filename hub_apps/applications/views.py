from django.core.mail import EmailMultiAlternatives #for sending mail with data passing to templates
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from hub_apps.jobs.models import Job
from hub_apps.profiles.models import UserProfile
from hub_apps.applications.models import JobApplication
from .forms import JobApplicationForm
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.paginator import Paginator
from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.urls import reverse

@login_required
def apply_for_job(request, job_id):
    job = get_object_or_404(Job, id=job_id) #filtering job based on job id to identify user want to apply for which job

    if request.user.is_recruiter:
        return redirect('list_jobs')  # Prevent recruiters from applying

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job #linking to job internally rather than asking from user
            application.applicant = request.user

            # Handle resume: Update profile only if a new resume is uploaded
            if 'resume' in request.FILES and request.FILES['resume']:
                profile, created = UserProfile.objects.get_or_create(user=request.user)
                profile.resume = request.FILES['resume']
                profile.save()

            application.save()

            # Send confirmation email
            current_site = get_current_site(request)
            protocol = 'https' if request.is_secure() else 'http'
            domain = current_site.domain
            subject = "Your Job Application Confirmation - CareerHub"
            html_message = render_to_string('emails/application_confirmation_email.html', {
                'applicant': request.user.username,
                'job_title': job.title,
                'company': job.company,
                'applied_at': application.applied_at,
                'protocol': protocol,
                'domain': domain,
            })
            plain_message = strip_tags(html_message) #converting HTML messages to plain text for backup if any mailbox doesnot support HTML
            email = EmailMultiAlternatives(subject, plain_message, 'carrerhub.com@gmail.com', [request.user.email])
            email.attach_alternative(html_message, "text/html") #attaching HTML message to email saying if HTML is supported show this fancy email
            email.send()

            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = JobApplicationForm()

    # Fallback for non-AJAX requests (not used by modal, but kept for completeness)
    return render(request, 'applications/apply.html', {'form': form, 'job': job})

@login_required
def view_applications(request):
    if not request.user.is_recruiter:
        return redirect('dashboard')  # Prevent job seekers from accessing this page

    jobs_posted = Job.objects.filter(posted_by=request.user)
    applications = JobApplication.objects.filter(job__in=jobs_posted)

    return render(request, 'applications/view_applications.html', {'applications': applications})


@login_required
def update_application_status(request, application_id):
    if request.method == 'POST' and request.user.is_recruiter:
        application = get_object_or_404(JobApplication, id=application_id, job__posted_by=request.user)
        
        # Only allow update if status is still "Pending"
        if application.status != "Pending":
            return HttpResponseRedirect(reverse('view_applications'))  # No change if already set

        # Determine new status from button clicked
        if 'accept' in request.POST:
            new_status = "Accepted"
        elif 'reject' in request.POST:
            new_status = "Rejected"
        else:
            return HttpResponseRedirect(reverse('view_applications'))  # Invalid action

        # Update status and save
        application.status = new_status
        application.save()

        # Send email notification
        subject = "Your Job Application Status Updated"
        html_message = render_to_string('emails/application_status_update.html', {
            'applicant': application.applicant.username,
            'job_title': application.job.title,
            'company': application.job.company,
            'status': new_status,
        })
        plain_message = strip_tags(html_message)
        email = EmailMultiAlternatives(subject, plain_message, 'your-email@gmail.com', [application.applicant.email])
        email.attach_alternative(html_message, "text/html")
        email.send()

        return HttpResponseRedirect(reverse('view_applications'))
    return HttpResponseRedirect(reverse('view_applications'))

@login_required
def track_applications(request):
    if request.user.is_recruiter:
        return redirect('dashboard')  # Recruiters shouldn't see this page

    applications = JobApplication.objects.filter(applicant=request.user).select_related('job')
    paginator = Paginator(applications, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'applications/track_applications.html', {'applications': applications,'page_obj':page_obj})

@login_required
def view_job_applicants(request, job_id):
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)  # Ensure only job owner can see applicants
    applications = JobApplication.objects.filter(job=job).select_related('applicant')

    return render(request, 'applications/view_job_applicants.html', {'job': job, 'applications': applications})
