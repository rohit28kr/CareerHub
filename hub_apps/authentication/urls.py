from django.urls import path
from django.contrib.auth import views as auth_views
from .views import register_user, login_user, logout_user, dashboard
from .forms import CustomPasswordResetForm

urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='authentication/password_reset.html',
        form_class=CustomPasswordResetForm,
        html_email_template_name='authentication/emails/password_reset_email.html'
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='authentication/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='authentication/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='authentication/password_reset_complete.html'
    ), name='password_reset_complete'),
]