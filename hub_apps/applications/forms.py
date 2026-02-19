from django import forms
from .models import JobApplication

class JobApplicationForm(forms.ModelForm):
    resume = forms.FileField(required=False, help_text="Upload your resume (optional if already in profile).")

    class Meta:
        model = JobApplication
        fields = ['cover_letter', 'resume']
