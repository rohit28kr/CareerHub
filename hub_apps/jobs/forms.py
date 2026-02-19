from django import forms
from .models import Job

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'location', 'job_type', 'salary']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'job_type': forms.Select(),  # Ensure Job Type is rendered as a dropdown
        }