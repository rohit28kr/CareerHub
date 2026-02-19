from django.db import models
from hub_apps.jobs.models import Job
from hub_apps.profiles.models import UserProfile 
from django.conf import settings #import settings to use auth user model as foreign key

class JobApplication(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE) #linking to Job model form hub_apps/jobs
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cover_letter = models.TextField(blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'), ('Rejected', 'Rejected')], default='Pending'
    )

    def __str__(self):
        return f"{self.applicant.username} applied for {self.job.title}"

    def get_resume(self):
        """Returns the resume from the applicant's profile."""
        profile = UserProfile.objects.get(user=self.applicant)
        return profile.resume.url if profile.resume else None  # Return resume URL if available
