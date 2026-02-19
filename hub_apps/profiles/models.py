from django.db import models
from django.conf import settings

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Job Seeker Fields
    resume = models.FileField(upload_to="resumes/", blank=True, null=True)
    skills = models.TextField(blank=True, null=True)
    experience = models.TextField(blank=True, null=True)
    education = models.TextField(blank=True, null=True)

    # Recruiter Fields
    company_name = models.CharField(max_length=255, blank=True, null=True)
    company_website = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.user.username
