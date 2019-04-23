"""recruitment_dashboard URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home)
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home)
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls))
"""
from django.conf.urls import url
from django.contrib import admin
from jobs import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.login_main, name='login'),
    url(r'logout/$', views.logout, name='logout'),
    url(r'resetpassword/$', views.reset_password, name='resetpassword'),
    url(r'^adminhome/$', views.admin_home, name='adminhome'),
    url(r'^userhome/$', views.user_home, name='userhome'),
    url(r'^adminlastmonth/$', views.admin_lastmonth, name='adminlastmonth'),
    url(r'^userlastmonth/$', views.user_lastmonth, name='userlastmonth'),    
    url(r'^editprofile/$', views.edit_profile, name='editprofile'),
    url(r'^createuser/$', views.create_user, name='createuser'),
    url(r'^addclient/$', views.add_client, name='addclient'),
    url(r'^addvendor/$', views.add_vendor, name='addvendor'),
    url(r'^addskills/$', views.add_skills, name='addskills'),
    url(r'^createjob/$', views.create_job, name='createjob'),
    url(r'^assignjob/$', views.assign_job, name='assignjob'),
    url(r'^changejobstatus/$', views.change_job_status, name='changejobstatus'),
    url(r'^generatechart/$', views.generate_chart, name='generatechart'),
    url(r'^generatereport/$', views.generate_report, name='generatereport'),
    url(r'^uploadresume/$', views.upload_resume, name='uploadresume'),
    url(r'^scheduleinterview/$', views.schedule_interview, name='scheduleinterview'),
    url(r'^searchresume/$', views.search_resume, name='searchresume'),
    url(r'^openrequirement/$', views.open_requirement, name='openrequirement'),
    url(r'^openrequirement/(?P<jobid>\d+)$', views.book_update, name='bookupdate'),
    url(r'^searchresume/(?P<candidateemail>\w+|[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$', views.resume_update, name='resumeupdate'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
