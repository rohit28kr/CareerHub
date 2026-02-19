from django.shortcuts import render
from hub_apps.jobs.models import Job


#rendring home page
def home(request):
    leatest_job = Job.objects.all()[:3]
    return render(request,'index.html',{'featured_jobs':leatest_job})