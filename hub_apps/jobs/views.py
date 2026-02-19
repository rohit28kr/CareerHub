from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import JobForm
from .models import Job
from django.core.paginator import Paginator
from hub_apps.applications.models import JobApplication  # Import JobApplication
from hub_apps.profiles.models import UserProfile
from django.contrib import messages
from .utils import export_accepted_applicants_to_excel, export_accepted_applicants_to_pdf

@login_required
def post_job(request):
    user = request.user  # Get logged-in user
    
    try:
        user_profile = UserProfile.objects.get(user=user)  # Ensure profile exists
    except UserProfile.DoesNotExist:
        messages.warning(request, "Please complete your profile before posting a job.")
        return redirect('edit_profile')  # Redirect user to complete their profile

    if not user.is_recruiter:
        return redirect('list_jobs')  # Only recruiters can post jobs

    # Check if company_name is missing or empty
    if not user_profile.company_name or user_profile.company_name.strip() == "":
        messages.warning(request, "You must provide a company name in your profile to post a job.")
        return redirect('edit_profile')

    # Pre-fill the form with company name
    initial_data = {'company': user_profile.company_name}

    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.company = user_profile.company_name  # Assign recruiter's company
            job.posted_by = user  # Link job to recruiter
            job.save()
            return redirect('list_jobs')
    else:
        form = JobForm(initial=initial_data)  # Pre-fill company name
    
    return render(request, 'jobs/post_job.html', {'form': form})

def list_jobs(request):
    # Base queryset: Start with all active jobs
    jobs = Job.objects.filter(is_active=True)

    # Restrict to jobs posted by the recruiter if user is authenticated and a recruiter
    if request.user.is_authenticated and request.user.is_recruiter:
        jobs = jobs.filter(posted_by=request.user)
    # Job seekers (authenticated, not recruiters) and anonymous users see all active jobs (no additional filter)

    # Get search query and filters from request
    search_query = request.GET.get('q', '')
    job_type_filter = request.GET.get('job_type', '')
    location_filter = request.GET.get('location', '')
    sort_option = request.GET.get('sort', 'newest')  # Default: Newest jobs first

    # Apply search filters
    if search_query:
        jobs = jobs.filter(title__icontains=search_query)
    if job_type_filter:
        jobs = jobs.filter(job_type=job_type_filter)
    if location_filter:
        jobs = jobs.filter(location__icontains=location_filter)

    # Apply sorting
    if sort_option == 'highest_salary':
        jobs = jobs.order_by('-salary')  # Highest salary first (nulls last implicitly)
    else:  # Default to newest
        jobs = jobs.order_by('-created_at')  # Newest jobs first

    # Pagination
    paginator = Paginator(jobs, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Add has_applied status for authenticated non-recruiter users (job seekers)
    if request.user.is_authenticated and not request.user.is_recruiter:
        applied_job_ids = JobApplication.objects.filter(applicant=request.user).values_list('job__id', flat=True)
        for job in page_obj:
            job.has_applied = job.id in applied_job_ids

    return render(request, 'jobs/list_jobs.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'job_type_filter': job_type_filter,
        'location_filter': location_filter,
        'sort_option': sort_option,
    })

@login_required
def edit_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)  # Ensure only the recruiter can edit

    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            return redirect('list_jobs')  # Redirect after saving changes
    else:
        form = JobForm(instance=job)

    return render(request, 'jobs/edit_job.html', {'form': form, 'job': job})

@login_required
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)  # Ensure only the recruiter can delete
    if request.method == 'POST':
        job.delete()
        return redirect('list_jobs')  # Redirect after deleting
    return render(request, 'jobs/confirm_delete.html', {'job': job})



@login_required
def export_accepted_applicants_excel(request):
    if not request.user.is_recruiter:
        return render(request, 'jobs/error.html', {'message': 'Only recruiters can export applicants.'})
    try:
        profile = UserProfile.objects.get(user=request.user)
        company_name = profile.company_name
        if not company_name:
            return render(request, 'jobs/error.html', {'message': 'Please set your company name in your profile.'})
    except UserProfile.DoesNotExist:
        return render(request, 'jobs/error.html', {'message': 'Please complete your profile.'})
    applications = JobApplication.objects.filter(
        job__company=company_name,
        status='Accepted'
    )
    if not applications.exists():
        return render(request, 'jobs/error.html', {'message': f'No accepted applicants found for {company_name}.'})
    return export_accepted_applicants_to_excel(applications, company_name)

@login_required
def export_accepted_applicants_pdf(request):
    if not request.user.is_recruiter:
        return render(request, 'jobs/error.html', {'message': 'Only recruiters can export applicants.'})
    try:
        profile = UserProfile.objects.get(user=request.user)
        company_name = profile.company_name
        if not company_name:
            return render(request, 'jobs/error.html', {'message': 'Please set your company name in your profile.'})
    except UserProfile.DoesNotExist:
        return render(request, 'jobs/error.html', {'message': 'Please complete your profile.'})
    applications = JobApplication.objects.filter(
        job__company=company_name,
        status='Accepted'
    )
    if not applications.exists():
        return render(request, 'jobs/error.html', {'message': f'No accepted applicants found for {company_name}.'})
    return export_accepted_applicants_to_pdf(applications, company_name)

@login_required
def export_accepted_applicants_by_job_excel(request, job_id):
    if not request.user.is_recruiter:
        return render(request, 'jobs/error.html', {'message': 'Only recruiters can export applicants.'})
    try:
        profile = UserProfile.objects.get(user=request.user)
        company_name = profile.company_name
        if not company_name:
            return render(request, 'jobs/error.html', {'message': 'Please set your company name in your profile.'})
    except UserProfile.DoesNotExist:
        return render(request, 'jobs/error.html', {'message': 'Please complete your profile.'})
    job = get_object_or_404(Job, id=job_id, company=company_name)
    applications = JobApplication.objects.filter(job=job, status='Accepted')
    if not applications.exists():
        return render(request, 'jobs/error.html', {'message': f'No accepted applicants found for {job.title}.'})
    return export_accepted_applicants_to_excel(applications, company_name)

@login_required
def export_accepted_applicants_by_job_pdf(request, job_id):
    if not request.user.is_recruiter:
        return render(request, 'jobs/error.html', {'message': 'Only recruiters can export applicants.'})
    try:
        profile = UserProfile.objects.get(user=request.user)
        company_name = profile.company_name
        if not company_name:
            return render(request, 'jobs/error.html', {'message': 'Please set your company name in your profile.'})
    except UserProfile.DoesNotExist:
        return render(request, 'jobs/error.html', {'message': 'Please complete your profile.'})
    job = get_object_or_404(Job, id=job_id, company=company_name)
    applications = JobApplication.objects.filter(job=job, status='Accepted')
    if not applications.exists():
        return render(request, 'jobs/error.html', {'message': f'No accepted applicants found for {job.title}.'})
    return export_accepted_applicants_to_pdf(applications, company_name)