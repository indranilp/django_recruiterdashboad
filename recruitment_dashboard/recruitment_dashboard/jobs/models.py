from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date

# Create your models here.
class Recruiter(AbstractUser):
    emailid = models.EmailField(null=True,blank=True)


class JobDetails(models.Model):
    class Meta:
        unique_together = (('clientname', 'positionname'),)
    clientname=models.CharField(max_length=200,null=True,blank=True)
    positionname  = models.CharField(max_length=200,null=True,blank=True)
    jobstatus = models.CharField(max_length=200)
    jobcreatedate = models.DateField(default=date.today())
    assignedto = models.CharField(max_length=50)

class ProfileDetails(models.Model):
    class Meta:
        unique_together = (('resourcename', 'resourcemail'),)
    clientname=models.CharField(max_length=200,null=True,blank=True)
    positionname  = models.CharField(max_length=200,null=True,blank=True)
    resourcename = models.CharField(max_length=200,null=True,blank=True)
    resourcemail = models.EmailField(null=True,blank=True)
    uploaddate = models.DateField()
    profilestatus = models.CharField(max_length=200,null=True,blank=True)
    submittedby = models.CharField(max_length=200, null=True, blank=True)

