from django import forms
from .models import UserProfile
from hub_apps.authentication.models import CustomUser

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        # Include all possible fields here, but we'll filter them dynamically
        fields = ['resume', 'skills', 'experience', 'education', 'company_name', 'company_website']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Get logged-in user
        super(UserProfileForm, self).__init__(*args, **kwargs)

        # Store the user for later use
        self.user = user

        if user:
            if user.is_recruiter:
                # Only show recruiter-specific fields
                self.fields = {
                    'company_name': forms.CharField(required=False, initial=self.instance.company_name if self.instance else ''),
                    'company_website': forms.URLField(required=False, initial=self.instance.company_website if self.instance else '')
                }
            else:
                # Only show job seeker-specific fields
                self.fields = {
                    'resume': forms.FileField(required=False, initial=self.instance.resume if self.instance else None),
                    'skills': forms.CharField(required=False, widget=forms.Textarea, initial=self.instance.skills if self.instance else ''),
                    'experience': forms.CharField(required=False, widget=forms.Textarea, initial=self.instance.experience if self.instance else ''),
                    'education': forms.CharField(required=False, widget=forms.Textarea, initial=self.instance.education if self.instance else '')
                }

    def save(self, commit=True):
        # Get the instance from the parent save method
        instance = super(UserProfileForm, self).save(commit=False)

        # Set the fields based on user type
        if self.user:
            if self.user.is_recruiter:
                instance.company_name = self.cleaned_data.get('company_name', '')
                instance.company_website = self.cleaned_data.get('company_website', '')
                # Clear job seeker fields
                instance.resume = None
                instance.skills = ''
                instance.experience = ''
                instance.education = ''
            else:
                instance.resume = self.cleaned_data.get('resume', None)
                instance.skills = self.cleaned_data.get('skills', '')
                instance.experience = self.cleaned_data.get('experience', '')
                instance.education = self.cleaned_data.get('education', '')
                # Clear recruiter fields
                instance.company_name = ''
                instance.company_website = ''

        if commit:
            instance.save()
        return instance

class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'profile_picture']