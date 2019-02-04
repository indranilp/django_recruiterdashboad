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
    openjobcount = JobDetails.objects.filter(jobstatus='open').filter(jobcreatedate=current_date).count()
    assignjobcount = JobDetails.objects.filter(jobstatus='assigned').filter(jobcreatedate=current_date).count()
    closejobcount = JobDetails.objects.filter(jobstatus='closed').filter(jobcreatedate=current_date).count()
    assignjobcount = JobDetails.objects.filter(jobstatus='assigned').filter(jobcreatedate=current_date).count()
    submitcount = ProfileDetails.objects.filter(profilestatus="submitted").filter(uploaddate=current_date).count()
    screencount = ProfileDetails.objects.filter(profilestatus="screened").filter(uploaddate=current_date).count()
    selectcount = ProfileDetails.objects.filter(profilestatus="selected").filter(uploaddate=current_date).count()

    submit_group1 = ProfileDetails.objects.all().filter(profilestatus="submitted").values('submittedby').annotate(
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
    chart_pie3 = pie_chart.render(is_unicode=True)

    return render_to_response('adminhome.html',{'currentuser': currentuser,'chart_pie1':chart_pie1,'chart_pie2':chart_pie2,'chart_pie3':chart_pie3,'closejobcount':closejobcount,'assignjobcount':assignjobcount,'openjobcount':openjobcount,'submitcount':submitcount,'screencount':screencount,'selectcount':selectcount},
                              context_instance=RequestContext(request))

def user_home(request):
    currentuser = request.session.get('name1')
    openjobcount = JobDetails.objects.filter(assignedto=currentuser).filter(jobstatus='open').filter(jobcreatedate=current_date).count()
    assignjobcount = JobDetails.objects.filter(assignedto=currentuser).filter(jobstatus='assigned').filter(jobcreatedate=current_date).count()
    closejobcount = JobDetails.objects.filter(assignedto=currentuser).filter(jobstatus='closed').filter(
        jobcreatedate=current_date).count()
    submitcount = ProfileDetails.objects.filter(submittedby=currentuser).filter(profilestatus="submitted").filter(uploaddate=current_date).count()
    screencount = ProfileDetails.objects.filter(submittedby=currentuser).filter(profilestatus="screened").filter(uploaddate=current_date).count()
    selectcount = ProfileDetails.objects.filter(submittedby=currentuser).filter(profilestatus="selected").filter(uploaddate=current_date).count()
    return render_to_response('userhome.html',{'currentuser': currentuser,'closejobcount':closejobcount,'assignjobcount':assignjobcount,'openjobcount':openjobcount,'submitcount':submitcount,'screencount':screencount,'selectcount':selectcount},
                              context_instance=RequestContext(request))

def generate_report(request):
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

        openjobcount = JobDetails.objects.filter(jobstatus='open').filter(jobcreatedate=current_date).count()
        assignjobcount = JobDetails.objects.filter(jobstatus='assigned').filter(jobcreatedate=current_date).count()
        submitcount = ProfileDetails.objects.filter(profilestatus="submitted").filter(uploaddate=current_date).count()
        screencount = ProfileDetails.objects.filter(profilestatus="screened").filter(uploaddate=current_date).count()
        selectcount = ProfileDetails.objects.filter(profilestatus="selected").filter(uploaddate=current_date).count()
        return render_to_response('generatereport.html', {'currentuser': currentuser, 'assignjobcount': assignjobcount,
                                                          'openjobcount': openjobcount, 'submitcount': submitcount,
                                                          'screencount': screencount, 'selectcount': selectcount,'bargraph':chart_line},
                                  context_instance=RequestContext(request))
    return render_to_response('generatereport.html',{'currentuser': currentuser},
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


def create_job(request):
    currentuser = request.session.get('name1')
    if request.POST:
        try :
                clientname = request.POST.get('clientname')
                positionname = request.POST.get('positionname')
                JobDetails.objects.create(clientname=clientname,positionname=positionname,jobstatus='open',assignedto='none',jobcreatedate=date.today())
                return render_to_response('success.html',{'currentuser': currentuser,'success': "Job created successfully"},
                                      context_instance=RequestContext(request))
        except Exception as error:
            return render_to_response('error.html',{'currentuser': currentuser,'error': error},
                                      context_instance=RequestContext(request))
    return render_to_response ('createjob.html',{'currentuser': currentuser},context_instance=RequestContext(request))

def assign_job(request):
    currentuser = request.session.get('name1')
    if request.POST:
        try :
                clientname = request.POST.get('clientname')
                positionname = request.POST.get('positionname')
                username = request.POST.get('username')
                res1=JobDetails.objects.filter(clientname=clientname).filter(positionname=positionname).update(jobstatus='assigned')
                print(clientname,positionname,username)
                print(res1)
                JobDetails.objects.filter(clientname=clientname).filter(positionname=positionname).update(
                    assignedto=username)
                return render_to_response('success.html',{'currentuser': currentuser,'success': "Job assigned successfully to recruiter " + username},
                                      context_instance=RequestContext(request))
        except Exception as error:
            return render_to_response('error.html',{'currentuser': currentuser,'error': error},
                                      context_instance=RequestContext(request))
    print()
    return render_to_response ('assignjob.html',{'currentuser': currentuser,'obj':JobDetails.objects.filter(jobstatus='open').values('clientname').distinct(),'obj1':JobDetails.objects.filter(jobstatus='open').values('positionname').distinct(),'obj2':Recruiter.objects.all().exclude(username='admin')},context_instance=RequestContext(request))

def change_job_status(request):
    currentuser = request.session.get('name1')
    if request.POST:
        try :
                clientname = request.POST.get('clientname')
                positionname = request.POST.get('positionname')
                jobstatus = request.POST.get('jobstatus')
                print(clientname,positionname,jobstatus)
                result=JobDetails.objects.filter(clientname=clientname).filter(positionname=positionname).update(jobstatus=jobstatus)
                print(result)
                return render_to_response('success.html',{'currentuser': currentuser,'success': "Job status changed successfully to  " + jobstatus},
                                      context_instance=RequestContext(request))
        except Exception as error:
            return render_to_response('error.html',{'currentuser': currentuser,'error': error},
                                      context_instance=RequestContext(request))
    return render_to_response ('changejobstatus.html',{'currentuser': currentuser,'obj':JobDetails.objects.values('clientname').distinct(),'obj1':JobDetails.objects.values('positionname').distinct(),'obj2':Recruiter.objects.all().exclude(username='admin')},context_instance=RequestContext(request))

def create_profile(request):
    currentuser = request.session.get('name1')
    if request.POST:
        try :
                clientname = request.POST.get('clientname')
                positionname = request.POST.get('positionname')
                resourcename = request.POST.get('resourcename')
                resourcemail = request.POST.get('resourcemail')

                ProfileDetails.objects.create(clientname=clientname,positionname=positionname,resourcename=resourcename,resourcemail=resourcemail,uploaddate=date.today(),profilestatus="submitted",submittedby=currentuser)
                return render_to_response('success.html',{'currentuser': currentuser,'success': "Profile created successfully"},
                                      context_instance=RequestContext(request))
        except Exception as error:
            return render_to_response('error.html',{'currentuser': currentuser,'error': error},
                                      context_instance=RequestContext(request))
    return render_to_response ('createprofile.html',{'currentuser': currentuser,'obj':JobDetails.objects.filter(jobstatus='assigned').filter(assignedto=currentuser).values('clientname').distinct(),'obj1':JobDetails.objects.filter(jobstatus='assigned').filter(assignedto=currentuser).values('positionname').distinct()},context_instance=RequestContext(request))

def change_profile_status(request):
    currentuser = request.session.get('name1')
    if request.POST:
        try :
                clientname = request.POST.get('clientname')
                positionname = request.POST.get('positionname')
                resourcename = request.POST.get('resourcename')
                profilestatus = request.POST.get('profilestatus')
                result=ProfileDetails.objects.filter(clientname=clientname).filter(positionname=positionname).filter(resourcename=resourcename).update(profilestatus=profilestatus)
                print(result)
                return render_to_response('success.html',{'currentuser': currentuser,'success': "Profile status for " + resourcename + " changed to " + profilestatus},
                                      context_instance=RequestContext(request))
        except Exception as error:
            return render_to_response('error.html',{'currentuser': currentuser,'error': error},
                                      context_instance=RequestContext(request))
    return render_to_response ('changeprofilestatus.html',{'currentuser': currentuser,'obj':JobDetails.objects.filter(jobstatus='assigned').filter(assignedto=currentuser).values('clientname').distinct(),'obj1':JobDetails.objects.filter(jobstatus='assigned').filter(assignedto=currentuser).values('positionname').distinct(),'obj2':ProfileDetails.objects.exclude(profilestatus="selected").filter(submittedby=currentuser).values('resourcename').distinct()},context_instance=RequestContext(request))