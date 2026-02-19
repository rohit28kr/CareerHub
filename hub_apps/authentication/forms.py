from django import forms
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm,PasswordResetForm
from .models import CustomUser
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from django.utils.http import urlsafe_base64_encode  
from django.utils.encoding import force_bytes

class UserRegistrationForm(UserCreationForm):
    is_recruiter = forms.BooleanField(required=False, label="Register as Recruiter")

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'profile_picture', 'password1', 'password2', 'is_recruiter']

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    

class CustomPasswordResetForm(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data["email"]
        # Check if the email exists and is tied to an active user
        if not CustomUser.objects.filter(email__iexact=email, is_active=True).exists():
            raise forms.ValidationError("There is no account associated with this email address.")
        return email
    
    def save(self, domain_override=None, subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.txt', use_https=False, token_generator=None,
             from_email=None, request=None, html_email_template_name=None, extra_email_context=None):
        email = self.cleaned_data["email"]
        active_users = self.get_users(email)
        for user in active_users:
            if not domain_override:
                from django.contrib.sites.shortcuts import get_current_site
                domain = get_current_site(request).domain
                protocol = 'https' if use_https else 'http'
            else:
                domain = domain_override
                protocol = 'http'

            context = {
                'user': user,
                'protocol': protocol,
                'domain': domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': token_generator.make_token(user),
                'token_expiry_hours': 24,  # Default Django token expiry
            }
            context.update(extra_email_context or {})

            subject = "Reset Your CareerHub Password"
            html_message = render_to_string('authentication/emails/password_reset_email.html', context)
            plain_message = strip_tags(html_message)

            email = EmailMultiAlternatives(
                subject, plain_message, from_email, [user.email]
            )
            email.attach_alternative(html_message, "text/html")
            email.send()