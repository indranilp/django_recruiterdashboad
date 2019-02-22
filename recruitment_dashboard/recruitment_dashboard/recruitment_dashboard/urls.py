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


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.login_main),
    url(r'^adminhome/$', views.admin_home),
    url(r'^userhome/$', views.user_home),
    url(r'^createuser/$', views.create_user),
    url(r'^addvendor/$', views.add_vendor),
    url(r'^addskill/$', views.add_skills),
    url(r'^createjob/$', views.create_job),
    url(r'^assignjob/$', views.assign_job),
    url(r'^changejobstatus/$', views.change_job_status),
    url(r'^generatereport/$', views.generate_report),
    url(r'^uploadresume/$', views.upload_resume),
    url(r'^scheduleinterview/$', views.schedule_interview),
    url(r'^searchresume/$', views.search_resume),

]