from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from .forms import UserRegistrationForm, UserLoginForm
from .models import CustomUser
from django.contrib.auth.decorators import login_required
from hub_apps.profiles.models import UserProfile
from hub_apps.applications.models import JobApplication
from hub_apps.jobs.models import Job
from django.core.paginator import Paginator
from hub_apps.profiles.forms import UserProfileForm
from django.contrib import messages

def register_user(request):
    if request.user.is_authenticated:  # Check if user is already logged in
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            messages.success(request, "Registration successful! Welcome to CareerHub.")  #  Success message
            login(request, user)  # Auto login after successful registration
            return redirect('dashboard')  
        else:
            messages.error(request, "There was an error with your registration. Please check the form.")  # Error message

    else:
        form = UserRegistrationForm()

    return render(request, 'authentication/register.html', {'form': form})

def login_user(request):
    if request.user.is_authenticated:  
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")  #  Show error message

    else:
        form = UserLoginForm()

    return render(request, 'authentication/login.html', {'form': form})

def logout_user(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    user = request.user
    user_profile, created = UserProfile.objects.get_or_create(user=user)

    # Ensure active_tab is set from the URL parameter, defaulting to 'overview'
    active_tab = request.GET.get('tab', 'overview')  # Always prioritize GET parameter

    if user.is_recruiter: 
        #logic for recruiter dashboard
        jobs = Job.objects.filter(posted_by=user)
        active_jobs_count = jobs.filter(is_active=True).count()
        total_applications = JobApplication.objects.filter(job__posted_by=user).count()
        pending_applications_count = JobApplication.objects.filter(job__posted_by=user, status='Pending').count()
        hired_count = JobApplication.objects.filter(job__posted_by=user, status='Accepted').count()
        recent_jobs = jobs.order_by('-created_at')[:3]
        recent_applications = JobApplication.objects.filter(job__posted_by=user).order_by('-applied_at')[:5]

        return render(request, 'authentication/recruiter_dashboard.html', {
            'profile': user_profile,
            'active_jobs_count': active_jobs_count,
            'total_applications': total_applications,
            'pending_applications_count': pending_applications_count,
            'hired_count': hired_count,
            'recent_jobs': recent_jobs,
            'recent_applications': recent_applications,
        })
    elif user.is_superuser:
        #if user is superuser redirecting to admin dashboard
        return redirect('admin:index')
    else:
        # Job Seeker Dashboard with Tabs
        # Overview Data
        applications = JobApplication.objects.filter(applicant=user)
        applications_count = applications.count()
        pending_applications_count = applications.filter(status='Pending').count()
        recent_applications = applications.order_by('-applied_at')[:5]
        saved_jobs_count = 0  # No SavedJob model; placeholder
        interviews_count = applications.filter(status='Accepted').count()
        applications_progress = min(applications_count * 10, 100)
        upcoming_interviews = applications.filter(status='Accepted').order_by('-applied_at')[:5]

        # Find Jobs Data
        jobs = Job.objects.filter(is_active=True)
        search_query = request.GET.get('q', '')
        job_type_filter = request.GET.get('job_type', '')
        location_filter = request.GET.get('location', '')
        sort_option = request.GET.get('sort', 'newest')

        if search_query:
            jobs = jobs.filter(title__icontains=search_query)
        if job_type_filter:
            jobs = jobs.filter(job_type=job_type_filter)
        if location_filter:
            jobs = jobs.filter(location__icontains=location_filter)
        if sort_option == 'highest_salary':
            jobs = jobs.order_by('-salary')
        else:
            jobs = jobs.order_by('-created_at')

        # Annotate jobs with has_applied status
        applied_job_ids = JobApplication.objects.filter(applicant=user).values_list('job_id', flat=True)
        jobs_list = []
        for job in jobs:
            job.has_applied = job.id in applied_job_ids
            jobs_list.append(job)

        jobs_paginator = Paginator(jobs_list, 5)
        jobs_page = request.GET.get('jobs_page', 1)
        jobs_page_obj = jobs_paginator.get_page(jobs_page)

        # Applications Data
        applications_paginator = Paginator(applications, 5)
        applications_page = request.GET.get('applications_page', 1)
        applications_page_obj = applications_paginator.get_page(applications_page)

        # Profile Forms
        if request.method == 'POST' and active_tab == 'profile':
            user_form = UserRegistrationForm(request.POST, request.FILES, instance=user)
            profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                return redirect(f'{request.path}?tab=profile')
        else:
            user_form = UserRegistrationForm(instance=user)
            profile_form = UserProfileForm(instance=user_profile)

        context = {
            'user': user,
            'profile': user_profile,
            'active_tab': active_tab,  # Pass active_tab to the template
            'applications_count': applications_count,
            'pending_applications_count': pending_applications_count,
            'saved_jobs_count': saved_jobs_count,
            'interviews_count': interviews_count,
            'applications_progress': applications_progress,
            'recent_applications': recent_applications,
            'upcoming_interviews': upcoming_interviews,
            'jobs': jobs_page_obj.object_list,
            'jobs_page_obj': jobs_page_obj,
            'search_query': search_query,
            'job_type_filter': job_type_filter,
            'location_filter': location_filter,
            'sort_option': sort_option,
            'applications': applications_page_obj.object_list,
            'applications_page_obj': applications_page_obj,
            'user_form': user_form,
            'profile_form': profile_form,
        }
        return render(request, 'authentication/jobseeker_dashboard.html', context)