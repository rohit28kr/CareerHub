from django.urls import path
from .views import apply_for_job, view_applications,update_application_status,track_applications,view_job_applicants

urlpatterns = [
    path('apply/<int:job_id>/', apply_for_job, name='apply_for_job'),
    path('view/', view_applications, name='view_applications'),  
    path('update_status/<int:application_id>/', update_application_status, name='update_application_status'),
    path('track/', track_applications, name='track_applications'),
    path('job/<int:job_id>/applicants/', view_job_applicants, name='view_job_applicants'),
]
