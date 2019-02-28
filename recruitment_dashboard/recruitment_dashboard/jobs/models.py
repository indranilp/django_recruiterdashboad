from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date

# Create your models here.
class Recruiter(AbstractUser):
    emailid = models.EmailField(null=True,blank=True)

class Vendor(models.Model):
    vendorname=models.CharField(max_length=200,primary_key=True)

class JobDetails(models.Model):
    jobid = models.IntegerField(primary_key=True)
    vendorname=models.ForeignKey(Vendor, on_delete=models.CASCADE)
    jobrole = models.CharField(max_length=200, null=True, blank=True)
    jobdescription = models.CharField(max_length=2000, null=True, blank=True)
    jobstatus = models.CharField(max_length=200)
    jobcreatedate = models.DateField(default=date.today())
    assignedto = models.CharField(max_length=200, null=True, blank=True)

class TechnicalSkills(models.Model):
    primaryskill = models.CharField(max_length=200,primary_key=True)

class Resume(models.Model):
    candidateemail = models.EmailField(primary_key=True)
    resume = models.FileField(upload_to='documents/')
    candidatename = models.CharField(max_length=200,null=True,blank=True)
    primaryskill = models.ForeignKey(TechnicalSkills, on_delete=models.CASCADE)
    submittedby = models.ForeignKey(Recruiter, on_delete=models.CASCADE)
    uploaddate = models.DateField(default=date.today())
    resumestatus = models.CharField(max_length=200, null=True, blank=True)

class Interview(models.Model):
    interviewid = models.IntegerField(primary_key=True)
    jobid = models.ForeignKey(JobDetails, on_delete=models.CASCADE)
    candidateemail = models.ForeignKey(Resume, on_delete=models.CASCADE)
    interviewdate   = models.DateField()
    interviewstatus = models.CharField(max_length=200,null=True,blank=True)


