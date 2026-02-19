from django.db import models
from django.conf import settings

class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('Full Time', 'Full Time'),
        ('Part Time', 'Part Time'),
        ('Freelance', 'Freelance'),
        ('Internship', 'Internship'),
    ]

    title = models.CharField(max_length=225)
    company = models.CharField(max_length=225)
    location = models.CharField(max_length=225)
    job_type = models.CharField(max_length=225, choices=JOB_TYPE_CHOICES, default='Full Time')
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True) 


    def __str__(self):
        return f"{self.title} at {self.company}"
