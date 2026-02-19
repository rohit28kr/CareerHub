from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class CustomUser(AbstractUser):
    is_recruiter = models.BooleanField(default=False)
    phone = models.CharField(max_length=15,blank=True,null=True)
    profile_picture = models.ImageField(upload_to="profile_pics/",blank=True,null=True)
    email = models.EmailField(unique=True)
    
    def __str__(self):
        return self.username
