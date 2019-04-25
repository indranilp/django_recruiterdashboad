from django import forms
from .models import *

class JobDetailsForm(forms.ModelForm):
    class Meta:
        model = JobDetails
        fields = ('jobid', 'jobtitle', 'contracttype', 'billrate', 'visapreference','jobcreatedate','assignedto','jobstatus',)

        
class ResumeDetailsForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ('candidateemail', 'candidatename', 'availability','resumestatus',)        