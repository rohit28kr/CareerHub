from django.urls import path
from .views import post_job, list_jobs, edit_job, delete_job, export_accepted_applicants_excel, export_accepted_applicants_pdf, export_accepted_applicants_by_job_excel, export_accepted_applicants_by_job_pdf

urlpatterns = [
    path('post/', post_job, name='post_job'),
    path('', list_jobs, name='list_jobs'),
    path('<int:job_id>/edit/', edit_job, name='edit_job'),
    path('<int:job_id>/delete/', delete_job, name='delete_job'),
    path('recruiter/export/accepted/excel/', export_accepted_applicants_excel, name='export_accepted_applicants_excel'),
    path('recruiter/export/accepted/pdf/', export_accepted_applicants_pdf, name='export_accepted_applicants_pdf'),
    path('recruiter/export/accepted/job/<int:job_id>/excel/', export_accepted_applicants_by_job_excel, name='export_accepted_applicants_by_job_excel'),
    path('recruiter/export/accepted/job/<int:job_id>/pdf/', export_accepted_applicants_by_job_pdf, name='export_accepted_applicants_by_job_pdf'),
]