from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import redirect
from jobs.models import *
from datetime import date
from datetime import datetime
import pygal
from django.db.models import Count
from django.db import connection, transaction
import pandas as pd

current_date = date.today()
current_month = datetime.now().month
current_year = datetime.now().year

def login_main(request):
    state = ''
    username = password = ''

    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                request.session['name1'] = username
                state = "You're successfully logged in!"
                if user.is_superuser:
                    return redirect('jobs.views.admin_home')
                else:
                    return redirect('jobs.views.user_home')
            else:
                state = "Your account is not active, please contact the site admin."
        else:
            state = "Invalid User name and/or Password."
    return render_to_response('login.html', {'state': state, 'username': username},
                              context_instance=RequestContext(request))

def admin_home(request):
    currentuser = request.session.get('name1')
    openjobcount = JobDetails.objects.filter(jobstatus='open').count()
    assignjobcount = JobDetails.objects.filter(jobstatus='assigned').count()
    closejobcount = JobDetails.objects.filter(jobstatus='closed').count()

    submitcount = Resume.objects.filter(resumestatus="submitted").count()
    screencount = Interview.objects.exclude(interviewstatus="selected").exclude(interviewstatus="rejected").count()
    selectcount = Interview.objects.filter(interviewstatus="selected").count()
    rejectcount = Interview.objects.filter(interviewstatus="rejected").count()

    '''submit_group1 = ProfileDetails.objects.all().filter(profilestatus="submitted").values('submittedby').annotate(
        total=Count('submittedby'))
    result1=[]
    for item in submit_group1:
        result1.append((item['total'],item['submittedby']))


    pie_chart = pygal.Pie(width=500, height=400, explicit_size=True)
    pie_chart.title = 'Submitted Today Data'
    for r in result1:
        pie_chart.add(r[1], [{'value': r[0], 'label': r[1]}])
    pie_chart.value_formatter = lambda x: "%.15f" % x
    chart_pie1 = pie_chart.render(is_unicode=True)

    submit_group2 = ProfileDetails.objects.all().filter(profilestatus="screened").values('submittedby').annotate(
        total=Count('submittedby'))
    result2 = []
    for item in submit_group2:
        result1.append((item['total'], item['submittedby']))

    pie_chart = pygal.Pie(width=500, height=400, explicit_size=True)
    pie_chart.title = 'Screened Today Data'
    for r in result2:
        pie_chart.add(r[1], [{'value': r[0], 'label': r[1]}])
    pie_chart.value_formatter = lambda x: "%.15f" % x
    chart_pie2 = pie_chart.render(is_unicode=True)

    submit_group3 = ProfileDetails.objects.all().filter(profilestatus="selected").values('submittedby').annotate(
        total=Count('submittedby'))
    result3 = []
    for item in submit_group3:
        result1.append((item['total'], item['submittedby']))

    pie_chart = pygal.Pie(width=500, height=400, explicit_size=True)
    pie_chart.title = 'Selected Today Data'
    for r in result3:
        pie_chart.add(r[1], [{'value': r[0], 'label': r[1]}])
    pie_chart.value_formatter = lambda x: "%.15f" % x
    chart_pie3 = pie_chart.render(is_unicode=True)'''

    return render_to_response('adminhome.html',{'currentuser': currentuser,'closejobcount':closejobcount,'assignjobcount':assignjobcount,'openjobcount':openjobcount,'submitcount':submitcount,'screencount':screencount,'selectcount':selectcount,'rejectcount':rejectcount},
                              context_instance=RequestContext(request))

def user_home(request):
    currentuser = request.session.get('name1')
    openjobcount = JobDetails.objects.filter(assignedto=currentuser).filter(jobstatus='open').filter(jobcreatedate=current_date).count()
    assignjobcount = JobDetails.objects.filter(assignedto=currentuser).filter(jobstatus='assigned').filter(jobcreatedate=current_date).count()
    closejobcount = JobDetails.objects.filter(assignedto=currentuser).filter(jobstatus='closed').filter(
        jobcreatedate=current_date).count()
    '''submitcount = ProfileDetails.objects.filter(submittedby=currentuser).filter(profilestatus="submitted").filter(uploaddate=current_date).count()
    screencount = ProfileDetails.objects.filter(submittedby=currentuser).filter(profilestatus="screened").filter(uploaddate=current_date).count()
    selectcount = ProfileDetails.objects.filter(submittedby=currentuser).filter(profilestatus="selected").filter(uploaddate=current_date).count()'''
    return render_to_response('userhome.html',{'currentuser': currentuser,'closejobcount':closejobcount,'assignjobcount':assignjobcount,'openjobcount':openjobcount},
                              context_instance=RequestContext(request))

def generate_chart(request):
    currentuser = request.session.get('name1')
    if request.POST:

        startdate = request.POST.get('startdate')
        enddate = request.POST.get('enddate')
        reporttype = request.POST.get('reporttype')
        print(startdate,enddate,reporttype)
        print(type(startdate))



        line_chart = pygal.Bar(width=1000, height=400, explicit_size=True)
        line_chart.title = 'Browser usage evolution (in %)'
        line_chart.x_labels = map(str, range(2002, 2013))
        line_chart.add('Firefox', [None, None, 0, 16.6, 25, 31, 36.4, 45.5, 46.3, 42.8, 37.1])
        line_chart.add('Chrome', [None, None, None, None, None, None, 0, 3.9, 10.8, 23.8, 35.3])
        line_chart.add('IE', [85.8, 84.6, 84.7, 74.5, 66, 58.6, 54.7, 44.8, 36.2, 26.6, 20.1])
        line_chart.add('Others', [14.2, 15.4, 15.3, 8.9, 9, 10.4, 8.9, 5.8, 6.7, 6.8, 7.5])
        chart_line=line_chart.render(is_unicode=True)

        return render_to_response('generatechart.html', {'currentuser': currentuser, 'bargraph':chart_line},
                                  context_instance=RequestContext(request))
    return render_to_response('generatechart.html',{'currentuser': currentuser},
                              context_instance=RequestContext(request))

def create_user(request):
    currentuser = request.session.get('name1')
    if request.POST:
        try :
                user_name = request.POST.get('username')
                email = request.POST.get('email')
                password = request.POST.get('password')
                rec =Recruiter.objects.create(username=user_name,email=email)
                rec_id = Recruiter.objects.get(username=user_name)
                rec_id.set_password(password)
                rec_id.save()
                return render_to_response('success.html',{'currentuser': currentuser,'success': "User created successfully"},
                                      context_instance=RequestContext(request))
        except Exception as error:
            return render_to_response('error.html',{'currentuser': currentuser,'error': error},
                                      context_instance=RequestContext(request))
    return render_to_response ('createuser.html',{'currentuser': currentuser},context_instance=RequestContext(request))

def add_vendor(request):
    currentuser = request.session.get('name1')
    if request.POST:
        try :
                vendorname = request.POST.get('vendorname')
                Vendor.objects.create(vendorname=vendorname)
                return render_to_response('success.html',{'currentuser': currentuser,'success': "Vendor created successfully"},
                                      context_instance=RequestContext(request))
        except Exception as error:
            return render_to_response('error.html',{'currentuser': currentuser,'error': error},
                                      context_instance=RequestContext(request))
    return render_to_response ('addvendor.html',{'currentuser': currentuser},context_instance=RequestContext(request))

def add_skills(request):
    currentuser = request.session.get('name1')
    if request.POST:
        try :
                skillname = request.POST.get('skillname')
                TechnicalSkills.objects.create(primaryskill=skillname)
                return render_to_response('success.html',{'currentuser': currentuser,'success': "Skills added successfully"},
                                      context_instance=RequestContext(request))
        except Exception as error:
            return render_to_response('error.html',{'currentuser': currentuser,'error': error},
                                      context_instance=RequestContext(request))
    return render_to_response ('addskill.html',{'currentuser': currentuser},context_instance=RequestContext(request))

def create_job(request):
    currentuser = request.session.get('name1')
    if request.POST:
        try :
                vendorname = request.POST.get('vendorname')
                jobrole = request.POST.get('jobrole')
                jobdescription = request.POST.get('jobdescription')
                vendorobj = Vendor.objects.get(vendorname=vendorname)
                JobDetails.objects.create(vendorname=vendorobj,jobrole=jobrole,jobdescription=jobdescription,jobstatus='open',assignedto='none',jobcreatedate=date.today())
                return render_to_response('success.html',{'currentuser': currentuser,'success': "Job created successfully"},
                                      context_instance=RequestContext(request))
        except Exception as error:
            return render_to_response('error.html',{'currentuser': currentuser,'error': error},
                                      context_instance=RequestContext(request))
    return render_to_response ('createjob.html',{'currentuser': currentuser,'obj':Vendor.objects.all()},context_instance=RequestContext(request))

def assign_job(request):
    currentuser = request.session.get('name1')
    if request.POST:
        try :
                vendorname = request.POST.get('vendorname')
                jobrole = request.POST.get('jobrole')
                username = request.POST.get('username')
                print(vendorname,jobrole,username)
                vendorobj = Vendor.objects.get(vendorname=vendorname)
                res1=JobDetails.objects.filter(vendorname_id=vendorname).filter(jobrole=jobrole).update(jobstatus='assigned')
                JobDetails.objects.filter(vendorname_id=vendorname).filter(jobrole=jobrole).update(
                    assignedto=username)
                return render_to_response('success.html',{'currentuser': currentuser,'success': "Job assigned successfully to Recruiter " + username},
                                      context_instance=RequestContext(request))
        except Exception as error:
            return render_to_response('error.html',{'currentuser': currentuser,'error': error},
                                      context_instance=RequestContext(request))
    return render_to_response ('assignjob.html',{'currentuser': currentuser,'obj':JobDetails.objects.filter(jobstatus='open').values('vendorname').distinct(),'obj1':JobDetails.objects.filter(jobstatus='open').values('jobrole').distinct(),'obj2':Recruiter.objects.all().exclude(username='admin'),'obj3':JobDetails.objects.all().filter(jobstatus='open')},context_instance=RequestContext(request))

def change_job_status(request):
    currentuser = request.session.get('name1')
    if request.POST:
        try :
                vendorname = request.POST.get('vendorname')
                jobrole = request.POST.get('jobrole')
                jobstatus = request.POST.get('jobstatus')
                print(vendorname,jobrole,jobstatus)
                result=JobDetails.objects.filter(vendorname_id=vendorname).filter(jobrole=jobrole).update(jobstatus=jobstatus)
                print(result)
                return render_to_response('success.html',{'currentuser': currentuser,'success': "Job status changed successfully to  " + jobstatus},
                                      context_instance=RequestContext(request))
        except Exception as error:
            return render_to_response('error.html',{'currentuser': currentuser,'error': error},
                                      context_instance=RequestContext(request))
    return render_to_response ('changejobstatus.html',{'currentuser': currentuser,'obj':JobDetails.objects.values('vendorname').distinct(),'obj1':JobDetails.objects.values('jobrole').distinct(),'obj2':Recruiter.objects.all().exclude(username='admin'),'obj3':JobDetails.objects.all()},context_instance=RequestContext(request))

def upload_resume(request):
    currentuser = request.session.get('name1')
    if request.POST:
        try :
                candidateemail = request.POST.get('candidateemail')
                candidatename = request.POST.get('candidatename')
                skillname = request.POST.get('skillname')
                #resume = request.POST.get('inputGroupFile01')
                recruiterobj = Recruiter.objects.get(username=currentuser)
                skillobj=TechnicalSkills.objects.get(primaryskill=skillname)
                Resume.objects.create(candidateemail=candidateemail,candidatename=candidatename,primaryskill=skillobj,resume=request.FILES['inputGroupFile01'],uploaddate=date.today(),resumestatus="submitted",submittedby=recruiterobj)
                return render_to_response('success.html',{'currentuser': currentuser,'success': "Resume uploaded successfully"},
                                      context_instance=RequestContext(request))
        except Exception as error:
            return render_to_response('error.html',{'currentuser': currentuser,'error': error},
                                      context_instance=RequestContext(request))
    return render_to_response ('uploadresume.html',{'currentuser': currentuser,'obj':TechnicalSkills.objects.all()},context_instance=RequestContext(request))

def schedule_interview(request):
    currentuser = request.session.get('name1')
    if request.POST:
        try :
                jobrole = request.POST.get('jobrole')
                vendorname = request.POST.get('vendorname')
                candidateemail = request.POST.get('candidateemail')                
                interviewdate = request.POST.get('startdate')
                temp_date=datetime.strptime(interviewdate, "%m/%d/%Y").date()
                interviewstatus = request.POST.get('interviewstatus')
                resumeobj = Resume.objects.get(candidateemail=candidateemail)
                jobobj = JobDetails.objects.get(vendorname=vendorname,jobrole=jobrole)                
                Interview.objects.create(jobid=jobobj,candidateemail=resumeobj,interviewdate=temp_date,interviewstatus=interviewstatus)
                return render_to_response('success.html',{'currentuser': currentuser,'success': "Interview scheduled for " + candidateemail},
                                      context_instance=RequestContext(request))
        except Exception as error:
            return render_to_response('error.html',{'currentuser': currentuser,'error': error},
                                      context_instance=RequestContext(request))
    '''return render_to_response('uploadresume.html', {'currentuser': currentuser,
                                                    'obj': JobDetails.objects.filter(jobstatus='assigned').filter(
                                                        assignedto=currentuser).values('clientname').distinct(),
                                                    'obj1': JobDetails.objects.filter(jobstatus='assigned').filter(
                                                        assignedto=currentuser).values('positionname').distinct()},
                              context_instance=RequestContext(request))'''

    return render_to_response ('scheduleinterview.html',{'currentuser': currentuser,'obj2':Resume.objects.all(),'obj3':JobDetails.objects.all().filter(assignedto=currentuser)},context_instance=RequestContext(request))


def search_resume(request):
    currentuser = request.session.get('name1')
    return render_to_response('searchresume.html', {'currentuser': currentuser, 'obj': Resume.objects.all()},
                              context_instance=RequestContext(request))

def generate_report(request):
    currentuser = request.session.get('name1')
    if request.POST:

        startdate = request.POST.get('startdate')
        enddate = request.POST.get('enddate')
        reporttype = request.POST.get('reporttype')
        print(startdate,enddate,reporttype)
        print(type(startdate))
        
                
        cursor = connection.cursor()

        cursor.execute('''SELECT count("jobs_interview"."interviewstatus"), "jobs_interview"."interviewstatus","jobs_jobdetails"."vendorname_id", "jobs_jobdetails"."jobrole", "jobs_jobdetails"."jobstatus", "jobs_jobdetails"."jobcreatedate", "jobs_jobdetails"."assignedto" FROM "jobs_jobdetails" LEFT OUTER JOIN "jobs_interview" ON ("jobs_jobdetails"."jobid" = "jobs_interview"."jobid_id") GROUP BY "jobs_jobdetails"."vendorname_id", "jobs_jobdetails"."jobrole","jobs_interview"."interviewstatus"''')
        rows = cursor.fetchall()
        final_dict={}

        final_dict1={}

        bdm_dict={}
        for item in rows:
           if item[4] != 'closed' :
                key = (item[2],item[3])
                if key not in final_dict:
                    final_dict[key]=[item[6],item[5],0,0,0,0]            
                if item[1] == 'None' :
                    final_dict[key][2] = item[0]
                if item[1] == 'round1' or item[1] == 'round2':
                    final_dict[key][3] += item[0]                
                if item[1] == 'selected':
                    final_dict[key][4] = item[0]
                if item[1] == 'rejected':
                    final_dict[key][5] = item[0]
        for key in final_dict:
            final_dict[key][2] = final_dict[key][3] + final_dict[key][4] + final_dict[key][5]



        for item in rows:
                key = (item[2],item[3])
                if key not in final_dict1:
                    final_dict1[key]=[item[6],item[5],0,0,0,0]            
                if item[1] == 'None' :
                    final_dict1[key][2] = item[0]
                if item[1] == 'round1' or item[1] == 'round2':
                    final_dict1[key][3] += item[0]                
                if item[1] == 'selected':
                    final_dict1[key][4] = item[0]
                if item[1] == 'rejected':
                    final_dict1[key][5] = item[0]
        for key in final_dict1:
            final_dict1[key][2] = final_dict1[key][3] + final_dict1[key][4] + final_dict1[key][5]
        print(final_dict1.values())
        columnnames = ['assign','date','source','screen','select','reject']
        df = pd.DataFrame.from_dict(final_dict1.values())
        df.columns = columnnames
        df['date'] = pd.to_datetime(df['date'])
        df.set_index(df["date"],inplace=True)
        print(df)
        df1=df.groupby('assign').resample('W').sum()
        print(df1)
        for item in rows:
            key = item[6]
            if key not in bdm_dict:            
                if item[4] != 'closed':
                    bdm_dict[key] = [1,0,0,0,0,1,0]
                else:
                    bdm_dict[key] = [1,0,0,0,0,0,1]
            else:
                bdm_dict[key][0] += 1
                if item[4] != 'closed':
                    bdm_dict[key][5] += 1  
                else:
                    bdm_dict[key][6] += 1

        for key in final_dict1:
            bdm_dict[final_dict1[key][0]][1] =  final_dict1[key][2]
            bdm_dict[final_dict1[key][0]][2] =  final_dict1[key][3]
            bdm_dict[final_dict1[key][0]][3] =  final_dict1[key][4]
            bdm_dict[final_dict1[key][0]][4] =  final_dict1[key][5]
        
        return render_to_response('generatereport.html', {'currentuser': currentuser, 'objdict':final_dict,'bdm_dict':bdm_dict},
                                  context_instance=RequestContext(request))    
    return render_to_response('selectdate.html', {'currentuser': currentuser},
                                  context_instance=RequestContext(request))        
