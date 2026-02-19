from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm, CustomUserForm
from .models import UserProfile

@login_required
def edit_profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = CustomUserForm(request.POST, request.FILES, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile, user=request.user)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('dashboard')  # Redirect to dashboard after update
        else:
            print("User Form Errors:", user_form.errors)  # Debugging output
            print("Profile Form Errors:", profile_form.errors)

    else:
        user_form = CustomUserForm(instance=request.user)
        profile_form = UserProfileForm(instance=user_profile, user=request.user)

    return render(request, 'profiles/edit_profile.html', {'user_form': user_form, 'profile_form': profile_form})
