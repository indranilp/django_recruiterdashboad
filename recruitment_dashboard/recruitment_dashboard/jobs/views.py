from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import redirect
from jobs.models import *
from datetime import date
from datetime import datetime,timedelta
import pygal
from django.db.models import Count
from django.db import connection, transaction
import pandas as pd
from django.contrib.auth.decorators import login_required
import json

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from jobs.forms import *


current_date = date.today()
current_month = datetime.now().month
current_year = datetime.now().year

def logout(request):
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
    else:
        state = 'you are successfully log out'
        session_keys = list(request.session.keys())
        for key in session_keys:
            del request.session[key]
    return render_to_response('login.html', {'state': state, 'username': username},
                              context_instance=RequestContext(request))

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

@login_required                              
def admin_home(request):
    currentuser = request.session.get('name1')
    current_month = datetime.now().month
    current_year = datetime.now().year
    openjobcount = JobDetails.objects.filter(jobcreatedate__month=current_month).filter(jobstatus='open').count()
    assignjobcount = JobDetails.objects.filter(jobcreatedate__month=current_month).filter(jobstatus='assigned').count()
    closejobcount = JobDetails.objects.filter(jobcreatedate__year=current_year).filter(jobcreatedate__month=current_month).filter(jobstatus='closed').count()

    submitcount = Resume.objects.filter(resumestatus="submitted").count()
    screencount = Interview.objects.exclude(interviewstatus="selected").exclude(interviewstatus="rejected").count()
    selectcount = Interview.objects.filter(interviewstatus="selected").count()
    rejectcount = Interview.objects.filter(interviewstatus="rejected").count()

    submit_group1 = JobDetails.objects.all().filter(jobcreatedate__year=current_year).filter(jobcreatedate__month=current_month).filter(jobstatus="closed").values('assignedto').annotate( total=Count('assignedto'))
    result1=[]
    for item in submit_group1:
        result1.append((item['total'],item['assignedto']))


    pie_chart = pygal.Pie(width=500, height=400, explicit_size=True)
    pie_chart.title = 'Hiring Assessment'
    for r in result1:
        pie_chart.add(r[1], [{'value': r[0], 'label': r[1]}])
    pie_chart.value_formatter = lambda x: "%.15f" % x
    chart_pie1 = pie_chart.render(is_unicode=True)
    
    cursor = connection.cursor()
    
    cursor.execute('''SELECT count("jobs_jobdetails"."vendorname_id"), "jobs_jobdetails"."vendorname_id", "jobs_jobdetails"."jobrole", "jobs_jobdetails"."assignedto" FROM "jobs_jobdetails" LEFT OUTER JOIN "jobs_interview" ON ("jobs_jobdetails"."jobid" = "jobs_interview"."jobid_id") WHERE strftime('%%m',"jobs_jobdetails"."jobcreatedate") = (%s) AND strftime('%%Y',"jobs_jobdetails"."jobcreatedate") = (%s) GROUP BY "jobs_jobdetails"."vendorname_id", "jobs_jobdetails"."jobrole", "jobs_jobdetails"."assignedto"''',(date.today().strftime('%m'),date.today().strftime('%Y')))
    
    rows = cursor.fetchall()

    graph_label_list=[]
    table_list = []
    b_chart = pygal.Bar(width=500, height=400, explicit_size=True)
    b_chart.title = "Submissions by Resource by Position"
    for item in rows:
        if item[3] not in graph_label_list:
            graph_label_list.append(item[3])
    b_chart.x_labels = graph_label_list    
    for item in rows:
        data_list = []
        for j in graph_label_list:
            data_list.append(0)
        for value in graph_label_list:
            if value in item:
                index = graph_label_list.index(value)
                data_list[index] = item[0]
        b_chart.add(item[1]+"/"+item[2], data_list)
        table_list.append(item)

    bar_graph1 = b_chart.render(is_unicode=True)
    #print table_list


    
    cursor.execute('''SELECT count("jobs_jobdetails"."vendorname_id"), "jobs_jobdetails"."vendorname_id" FROM "jobs_jobdetails" LEFT OUTER JOIN "jobs_interview" ON ("jobs_jobdetails"."jobid" = "jobs_interview"."jobid_id") WHERE strftime('%%m',"jobs_jobdetails"."jobcreatedate") = (%s) AND strftime('%%Y',"jobs_jobdetails"."jobcreatedate") = (%s) GROUP BY "jobs_jobdetails"."vendorname_id" ''',(date.today().strftime('%m'),date.today().strftime('%Y')))
    
    rows1 = cursor.fetchall()

    
    b_chart1 = pygal.HorizontalBar(width=500, height=400, explicit_size=True)
    b_chart1.title = "Pipeline of Positions"
    for item in rows1:        
        b_chart1.add(item[1], [item[0]])
    bar_graph2 = b_chart1.render(is_unicode=True)
    
    funnel_list=[]
    for item in rows1:
        funnel_row={}
        funnel_row['y'] = item[0]
        funnel_row['label'] = item[1]
        funnel_list.append(funnel_row)
    data = json.dumps(funnel_list)
    
    


    return render_to_response('adminhome.html',{'currentuser': currentuser,'userobject':Recruiter.objects.get(username=currentuser),'closejobcount':closejobcount,'assignjobcount':assignjobcount,'openjobcount':openjobcount,'submitcount':submitcount,'screencount':screencount,'selectcount':selectcount,'rejectcount':rejectcount,'chart_pie1':chart_pie1,'bar_graph1':bar_graph1,'bar_graph2':bar_graph2,'table_list':table_list,'data':data},
                              context_instance=RequestContext(request))
                              
@login_required                              
def admin_lastmonth(request):
    currentuser = request.session.get('name1')
    today = date.today()
    last_day_previous_month = today - timedelta(days=today.day)
    same_day_last_month = last_day_previous_month.replace(day=today.day)
    previous_month = same_day_last_month.month
    previous_year = same_day_last_month.year
    openjobcount = JobDetails.objects.filter(jobcreatedate__month=previous_month).filter(jobstatus='open').count()
    assignjobcount = JobDetails.objects.filter(jobcreatedate__month=previous_month).filter(jobstatus='assigned').count()
    closejobcount = JobDetails.objects.filter(jobcreatedate__year=previous_year).filter(jobcreatedate__month=previous_month).filter(jobstatus='closed').count()

    submitcount = Resume.objects.filter(resumestatus="submitted").count()
    screencount = Interview.objects.exclude(interviewstatus="selected").exclude(interviewstatus="rejected").count()
    selectcount = Interview.objects.filter(interviewstatus="selected").count()
    rejectcount = Interview.objects.filter(interviewstatus="rejected").count()

    submit_group1 = JobDetails.objects.all().filter(jobcreatedate__year=previous_year).filter(jobcreatedate__month=previous_month).filter(jobstatus="closed").values('assignedto').annotate( total=Count('assignedto'))
    result1=[]
    for item in submit_group1:
        result1.append((item['total'],item['assignedto']))


    pie_chart = pygal.Pie(width=500, height=400, explicit_size=True)
    pie_chart.title = 'Hiring Assessment'
    for r in result1:
        pie_chart.add(r[1], [{'value': r[0], 'label': r[1]}])
    pie_chart.value_formatter = lambda x: "%.15f" % x
    chart_pie1 = pie_chart.render(is_unicode=True)

    cursor = connection.cursor()

    cursor.execute('''SELECT count("jobs_jobdetails"."vendorname_id"), "jobs_jobdetails"."vendorname_id", "jobs_jobdetails"."jobrole", "jobs_jobdetails"."assignedto" FROM "jobs_jobdetails" LEFT OUTER JOIN "jobs_interview" ON ("jobs_jobdetails"."jobid" = "jobs_interview"."jobid_id") WHERE strftime('%%m',"jobs_jobdetails"."jobcreatedate") = (%s) AND strftime('%%Y',"jobs_jobdetails"."jobcreatedate") = (%s) GROUP BY "jobs_jobdetails"."vendorname_id", "jobs_jobdetails"."jobrole", "jobs_jobdetails"."assignedto"''',(same_day_last_month.strftime('%m'),same_day_last_month.strftime('%Y')))
    
    
    rows = cursor.fetchall()

    graph_label_list=[]
    table_list = []
    b_chart = pygal.Bar(width=500, height=400, explicit_size=True)
    b_chart.title = "Submissions by Resource by Position"
    for item in rows:
        if item[3] not in graph_label_list:
            graph_label_list.append(item[3])
    b_chart.x_labels = graph_label_list    
    for item in rows:
        data_list = []
        for j in graph_label_list:
            data_list.append(0)
        for value in graph_label_list:
            if value in item:
                index = graph_label_list.index(value)
                data_list[index] = item[0]
        b_chart.add(item[1]+"/"+item[2], data_list)
        table_list.append(item)

    bar_graph1 = b_chart.render(is_unicode=True)


    
    cursor.execute('''SELECT count("jobs_jobdetails"."vendorname_id"), "jobs_jobdetails"."vendorname_id" FROM "jobs_jobdetails" LEFT OUTER JOIN "jobs_interview" ON ("jobs_jobdetails"."jobid" = "jobs_interview"."jobid_id") WHERE strftime('%%m',"jobs_jobdetails"."jobcreatedate") = (%s) AND strftime('%%Y',"jobs_jobdetails"."jobcreatedate") = (%s) GROUP BY "jobs_jobdetails"."vendorname_id" ''',(same_day_last_month.strftime('%m'),same_day_last_month.strftime('%Y')))
    
    rows1 = cursor.fetchall()

    
    b_chart1 = pygal.HorizontalBar(width=500, height=400, explicit_size=True)
    b_chart1.title = "Pipeline of Positions"
    for item in rows1:        
        b_chart1.add(item[1], [item[0]])
    bar_graph2 = b_chart1.render(is_unicode=True)

    funnel_list=[]
    for item in rows1:
        funnel_row={}
        funnel_row['y'] = item[0]
        funnel_row['label'] = item[1]
        funnel_list.append(funnel_row)
    data = json.dumps(funnel_list)
    return render_to_response('adminhome.html',{'currentuser': currentuser,'userobject':Recruiter.objects.get(username=currentuser),'closejobcount':closejobcount,'assignjobcount':assignjobcount,'openjobcount':openjobcount,'submitcount':submitcount,'screencount':screencount,'selectcount':selectcount,'rejectcount':rejectcount,'chart_pie1':chart_pie1,'bar_graph1':bar_graph1,'bar_graph2':bar_graph2,'table_list':table_list,'data':data},
                              context_instance=RequestContext(request))                              

@login_required                              
def user_home(request):
    currentuser = request.session.get('name1')    
    current_month = datetime.now().month
    current_year = datetime.now().year
    closejobcount = JobDetails.objects.filter(assignedto=currentuser).filter(jobcreatedate__year=current_year).filter(jobcreatedate__month=current_month).filter(jobstatus='closed').count()
    return render_to_response('userhome.html',{'currentuser': currentuser,'userobject':Recruiter.objects.get(username=currentuser),'closejobcount':closejobcount},
                              context_instance=RequestContext(request))
                              
@login_required                              
def user_lastmonth(request):
    currentuser = request.session.get('name1')
    today = date.today()
    last_day_previous_month = today - timedelta(days=today.day)
    same_day_last_month = last_day_previous_month.replace(day=today.day)
    previous_month = same_day_last_month.month
    previous_year = same_day_last_month.year
    currentuser = request.session.get('name1')
    closejobcount = JobDetails.objects.filter(assignedto=currentuser).filter(jobcreatedate__year=previous_year).filter(jobcreatedate__month=previous_month).filter(jobstatus='closed').count()
    
    return render_to_response('userhome.html',{'currentuser': currentuser,'userobject':Recruiter.objects.get(username=currentuser),'closejobcount':closejobcount},
                              context_instance=RequestContext(request))                              

@login_required                              
def generate_chart(request):
    currentuser = request.session.get('name1')
    if request.POST:

        startdate = request.POST.get('startdate')
        enddate = request.POST.get('enddate')
        reporttype = request.POST.get('reporttype')
        
        cursor = connection.cursor()

        cursor.execute('''SELECT count("jobs_interview"."interviewstatus"), "jobs_interview"."interviewstatus","jobs_jobdetails"."vendorname_id", "jobs_jobdetails"."jobrole", "jobs_jobdetails"."jobstatus", "jobs_jobdetails"."jobcreatedate", "jobs_jobdetails"."assignedto" FROM "jobs_jobdetails" LEFT OUTER JOIN "jobs_interview" ON ("jobs_jobdetails"."jobid" = "jobs_interview"."jobid_id") WHERE "jobs_jobdetails"."jobcreatedate" >= (%s) AND "jobs_jobdetails"."jobcreatedate" <= (%s) GROUP BY "jobs_jobdetails"."vendorname_id", "jobs_jobdetails"."jobrole","jobs_interview"."interviewstatus"''',(datetime.strptime(startdate, '%m/%d/%Y').strftime('%Y-%m-%d'),datetime.strptime(enddate, '%m/%d/%Y').strftime('%Y-%m-%d')))
        rows = cursor.fetchall()

        final_dict1={}

        bdm_dict={}
        #print rows
        report1 = []
        if len(rows) != 0:

            for item in rows:
                    key = (item[2],item[3],item[4])
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
            final_list = []
            for key,values in final_dict1.items():
                final_list.append([key[0],key[1],key[2],values[0],values[1],values[2],values[3],values[4],values[5]])

            columnnames = ['client','jobrole','jobstatus','assign','date','source','screen','select','reject']
            df = pd.DataFrame.from_dict(final_list)
            df.columns = columnnames
            df['date'] = pd.to_datetime(df['date'])
            df.set_index(df["date"],inplace=True)

            df1=df.groupby(['client','jobrole','assign','jobstatus']).resample('D').sum()
            if reporttype == 'daily':
                df2=df.groupby(['assign','jobstatus']).resample('D').sum()
            elif reporttype == 'weekly':
                df2=df.groupby(['assign','jobstatus']).resample('W').sum()
            elif reporttype == 'monthly':
                df2=df.groupby(['assign','jobstatus']).resample('M').sum()
            # print(df1)
            #print(df2)

            for name in df1.index:         
                list1 = [name[0],name[1], name[2], name[3], name[4],df1.loc[name].values[0],df1.loc[name].values[1],df1.loc[name].values[2],df1.loc[name].values[3]]
                report1.append(list1) 
            # print(report1)
            report2 = []
            for name in df2.index:
                if name[0] != 'none':            
                    list2=[name[0],name[1],name[2].date(),df2.loc[name].values[0],df2.loc[name].values[1],df2.loc[name].values[2],df2.loc[name].values[3]]
                    report2.append(list2)
            # print("report2")    
            # print(report2)
            graph_dict={}
            for item in report2:
                key = item[0]
                graph_key = item[2]                   
                if graph_key not in graph_dict:
                    graph_dict[graph_key] = {}
                    graph_dict[graph_key][item[0]]=[]
                else:
                    graph_dict[graph_key][item[0]] = []
                if key not in bdm_dict:            
                    if item[1] != 'closed':
                        bdm_dict[key] = [1,0,0,0,0,1,0]
                    else:
                        bdm_dict[key] = [1,0,0,0,0,0,1]
                else:
                    bdm_dict[key][0] += 1
                    if item[1] != 'closed':
                        bdm_dict[key][5] += 1  
                    else:
                        bdm_dict[key][6] += 1

            for key in final_dict1:
                if final_dict1[key][0] != 'none':   
                    bdm_dict[final_dict1[key][0]][1] +=  final_dict1[key][2]
                    bdm_dict[final_dict1[key][0]][2] +=  final_dict1[key][3]
                    bdm_dict[final_dict1[key][0]][3] +=  final_dict1[key][4]
                    bdm_dict[final_dict1[key][0]][4] +=  final_dict1[key][5]    
            # print("====bdmdict====")                   
            # print(bdm_dict)
            # print(graph_dict)
            for key,values in graph_dict.items():
                for item in report2:
                    if item[2] == key:
                            graph_dict[key][item[0]].append(item[3])  
                            graph_dict[key][item[0]].append(item[4])
                            graph_dict[key][item[0]].append(item[5])
                            graph_dict[key][item[0]].append(item[6])
            # print(graph_dict)



        line_chart = pygal.Bar(width=1000, height=400, explicit_size=True)
        line_chart.title =  str(reporttype.upper()) + ' BDM Report for Resume Source'
        graph_label_list = []
        for item in graph_dict.keys():
            if reporttype == 'daily':
                graph_label_list.append(item)
            elif reporttype == 'weekly':
                graph_label_list.append("Week" + item.strftime("%V"))
            elif reporttype == 'monthly':
                graph_label_list.append(item.strftime("%B"))
        line_chart.x_labels = graph_label_list
        data_dict={}
        for key,values in graph_dict.items():       
            for item in bdm_dict:
                if item not in data_dict:
                    data_dict[item] = []
                if item in values.keys():
                    data_dict[item].append(values[item][0])
                else:
                    data_dict[item].append(0)
        # print(data_dict)
        for k,v in data_dict.items():             
            line_chart.add(k,v)
        chart_line=line_chart.render(is_unicode=True)

        
        line_chart1 = pygal.Bar(width=1000, height=400, explicit_size=True)
        line_chart1.title =  str(reporttype.upper()) + ' BDM Report for Resume Screen'
        graph_label_list = []
        for item in graph_dict.keys():
            if reporttype == 'daily':
                graph_label_list.append(item)
            elif reporttype == 'weekly':
                graph_label_list.append("Week" + item.strftime("%V"))
            elif reporttype == 'monthly':
                graph_label_list.append(item.strftime("%B"))
        line_chart1.x_labels = graph_label_list
        data_dict={}
        for key,values in graph_dict.items():       
            for item in bdm_dict:
                if item not in data_dict:
                    data_dict[item] = []
                if item in values.keys():
                    data_dict[item].append(values[item][0])
                else:
                    data_dict[item].append(0)
        # print(data_dict)
        for k,v in data_dict.items():             
            line_chart1.add(k,v)
        chart_line1=line_chart1.render(is_unicode=True)
        
        
        line_chart2 = pygal.Bar(width=1000, height=400, explicit_size=True)
        line_chart2.title =  str(reporttype.upper()) + ' BDM Report for Candidate Selected'
        graph_label_list = []
        for item in graph_dict.keys():
            if reporttype == 'daily':
                graph_label_list.append(item)
            elif reporttype == 'weekly':
                graph_label_list.append("Week" + item.strftime("%V"))
            elif reporttype == 'monthly':
                graph_label_list.append(item.strftime("%B"))
        line_chart2.x_labels = graph_label_list
        data_dict={}
        for key,values in graph_dict.items():       
            for item in bdm_dict:
                if item not in data_dict:
                    data_dict[item] = []
                if item in values.keys():
                    data_dict[item].append(values[item][2])
                else:
                    data_dict[item].append(0)
        # print(data_dict)
        for k,v in data_dict.items():             
            line_chart2.add(k,v)
        chart_line2=line_chart2.render(is_unicode=True)
        
        line_chart3 = pygal.Bar(width=1000, height=400, explicit_size=True)
        line_chart3.title =  str(reporttype.upper()) + ' BDM Report for Resume Rejected'
        graph_label_list = []
        for item in graph_dict.keys():
            if reporttype == 'daily':
                graph_label_list.append(item)
            elif reporttype == 'weekly':
                graph_label_list.append("Week" + item.strftime("%V"))
            elif reporttype == 'monthly':
                graph_label_list.append(item.strftime("%B"))
        line_chart3.x_labels = graph_label_list
        data_dict={}
        for key,values in graph_dict.items():       
            for item in bdm_dict:
                if item not in data_dict:
                    data_dict[item] = []
                if item in values.keys():
                    data_dict[item].append(values[item][3])
                else:
                    data_dict[item].append(0)
        # print(data_dict)
        for k,v in data_dict.items():             
            line_chart3.add(k,v)
        chart_line3=line_chart3.render(is_unicode=True)
        
        return render_to_response('generatechart.html', {'currentuser': currentuser, 'userobject':Recruiter.objects.get(username=currentuser),'bargraph':chart_line,'bargraph1':chart_line1,'bargraph2':chart_line2,'bargraph3':chart_line3,'bdm_dict':bdm_dict},
                                  context_instance=RequestContext(request))
    return render_to_response('generatechart.html',{'currentuser': currentuser,'userobject':Recruiter.objects.get(username=currentuser)},
                              context_instance=RequestContext(request))

@login_required                              
def create_user(request):
    currentuser = request.session.get('name1')
    if request.POST:
        try :
                user_name = request.POST.get('username')
                email = request.POST.get('email')
                password = request.POST.get('password')
                gender = request.POST.get('gender')
                designation = request.POST.get('designation')
                mobile = request.POST.get('mobile')
                birthdate = request.POST.get('birthdate')                
                temp_date=datetime.strptime(birthdate, "%m/%d/%Y").date()
                rec =Recruiter.objects.create(username=user_name,email=email,gender=gender,designation=designation,birthdate=temp_date,mobile=mobile,picfile = request.FILES['pic'])
                rec_id = Recruiter.objects.get(username=user_name)
                rec_id.set_password(password)
                rec_id.save()
                return render_to_response('success.html',{'currentuser': currentuser,'userobject':Recruiter.objects.get(username=currentuser),'success': "User created successfully"},
                                      context_instance=RequestContext(request))
        except Exception as error:
            return render_to_response('error.html',{'currentuser': currentuser, 'userobject':Recruiter.objects.get(username=currentuser),'error': error},
                                      context_instance=RequestContext(request))
    return render_to_response ('createuser.html',{'currentuser': currentuser,'userobject':Recruiter.objects.get(username=currentuser)},context_instance=RequestContext(request))
    
@login_required                              
def edit_profile(request):
    currentuser = request.session.get('name1')

    if request.POST:
        try :
                user_name = request.POST.get('username1')
                email = request.POST.get('email1')
                #password = request.POST.get('password1')
                gender = request.POST.get('gender1')
                designation = request.POST.get('designation1')
                mobile = request.POST.get('mobile1')
                #birthdate = request.POST.get('birthdate1')                
                #temp_date=datetime.strptime(birthdate, "%m/%d/%Y").date()
                
                rec_id = Recruiter.objects.get(username=currentuser)
                print(rec_id)
              
                rec_id.email=email
                rec_id.gender=gender
                rec_id.mobile=mobile
                rec_id.designation=designation
                #rec_id.temp_date=temp_date
                rec_id.picfile=request.FILES['pic1']
                #rec_id.set_password(password)
                rec_id.save()
                return render_to_response('success.html',{'currentuser': currentuser,'userobject':Recruiter.objects.get(username=currentuser),'success': "User updated successfully"},
                                      context_instance=RequestContext(request))
        except Exception as error:
            return render_to_response('error.html',{'currentuser': currentuser,'userobject':Recruiter.objects.get(username=currentuser),'error': error},
                                      context_instance=RequestContext(request))
    return render_to_response ('updateuser.html',{'currentuser': currentuser,'userobject':Recruiter.objects.get(username=currentuser)},context_instance=RequestContext(request))    

@login_required
def add_vendor(request):
    currentuser = request.session.get('name1')
    if request.POST:
        try :
                vendorname = request.POST.get('vendorname')
                Vendor.objects.create(vendorname=vendorname)
                return render_to_response('success.html',{'currentuser': currentuser,'userobject':Recruiter.objects.get(username=currentuser),'success': "Vendor created successfully"},
                                      context_instance=RequestContext(request))
        except Exception as error:
            return render_to_response('error.html',{'currentuser': currentuser,'userobject':Recruiter.objects.get(username=currentuser),'error': error},
                                      context_instance=RequestContext(request))
    return render_to_response ('addvendor.html',{'currentuser': currentuser,'userobject':Recruiter.objects.get(username=currentuser)},context_instance=RequestContext(request))

@login_required    
def add_skills(request):
    currentuser = request.session.get('name1')
    if request.POST:
        try :
                skillname = request.POST.get('skillname')
                TechnicalSkills.objects.create(primaryskill=skillname)
                return render_to_response('success.html',{'currentuser': currentuser,'userobject':Recruiter.objects.get(username=currentuser),'success': "Skills added successfully"},
                                      context_instance=RequestContext(request))
        except Exception as error:
            return render_to_response('error.html',{'currentuser': currentuser,'userobject':Recruiter.objects.get(username=currentuser),'error': error},
                                      context_instance=RequestContext(request))
    return render_to_response ('addskill.html',{'currentuser': currentuser,'userobject':Recruiter.objects.get(username=currentuser)},context_instance=RequestContext(request))

@login_required    
def create_job(request):
    currentuser = request.session.get('name1')
    if request.POST:
        try :
                vendorname = request.POST.get('vendorname')
                jobrole = request.POST.get('jobrole')
                jobdescription = request.POST.get('jobdescription')
                contracttype = request.POST.get('contracttype')
                clientrate = request.POST.get('clientrate')
                visapreference = request.POST.get('visapreference')
                vendorobj = Vendor.objects.get(vendorname=vendorname)    
                JobDetails.objects.create(vendorname=vendorobj,jobrole=jobrole,contracttype=contracttype,clientrate=clientrate,visapreference=visapreference,jobdescription=jobdescription,jobstatus='open',assignedto='none',jobcreatedate=date.today())
                return render_to_response('success.html',{'currentuser': currentuser,'userobject':Recruiter.objects.get(username=currentuser),'success': "Job created successfully"},
                                      context_instance=RequestContext(request))
        except Exception as error:
            return render_to_response('error.html',{'currentuser': currentuser,'userobject':Recruiter.objects.get(username=currentuser),'error': error},
                                      context_instance=RequestContext(request))
    return render_to_response ('createjob.html',{'currentuser': currentuser,'userobject':Recruiter.objects.get(username=currentuser),'obj':Vendor.objects.all()},context_instance=RequestContext(request))

@login_required    
def assign_job(request):
    currentuser = request.session.get('name1')
    if request.POST:
        try :
                vendorname = request.POST.get('vendorname')
                jobrole = request.POST.get('jobrole')
                username = request.POST.get('username')
                #print(vendorname,jobrole,username)
                vendorobj = Vendor.objects.get(vendorname=vendorname)
                res1=JobDetails.objects.filter(vendorname_id=vendorname).filter(jobrole=jobrole).update(jobstatus='assigned')
                JobDetails.objects.filter(vendorname_id=vendorname).filter(jobrole=jobrole).update(
                    assignedto=username)
                return render_to_response('success.html',{'currentuser': currentuser,'obj1':Recruiter.objects.get(username=currentuser),'success': "Job assigned successfully to Recruiter " + username},
                                      context_instance=RequestContext(request))
        except Exception as error:
            return render_to_response('error.html',{'currentuser': currentuser,'error': error},
                                      context_instance=RequestContext(request))
    return render_to_response ('assignjob.html',{'currentuser': currentuser,'obj':JobDetails.objects.filter(jobstatus='open').values('vendorname').distinct(),'obj1':JobDetails.objects.filter(jobstatus='open').values('jobrole').distinct(),'obj2':Recruiter.objects.all().exclude(username='admin'),'obj3':JobDetails.objects.all().filter(jobstatus='open')},context_instance=RequestContext(request))

@login_required    
def change_job_status(request):
    currentuser = request.session.get('name1')
    if request.POST:
        try :
                vendorname = request.POST.get('vendorname')
                jobrole = request.POST.get('jobrole')
                jobstatus = request.POST.get('jobstatus')
                #print(vendorname,jobrole,jobstatus)
                result=JobDetails.objects.filter(vendorname_id=vendorname).filter(jobrole=jobrole).update(jobstatus=jobstatus)
                #print(result)
                return render_to_response('success.html',{'currentuser': currentuser,'userobject':Recruiter.objects.get(username=currentuser),'success': "Job status changed successfully to  " + jobstatus},
                                      context_instance=RequestContext(request))
        except Exception as error:
            return render_to_response('error.html',{'currentuser': currentuser,'userobject':Recruiter.objects.get(username=currentuser),'error': error},
                                      context_instance=RequestContext(request))
    return render_to_response ('changejobstatus.html',{'currentuser': currentuser,'userobject':Recruiter.objects.get(username=currentuser),'obj':JobDetails.objects.values('vendorname').distinct(),'obj1':JobDetails.objects.values('jobrole').distinct(),'obj2':Recruiter.objects.all().exclude(username='admin'),'obj3':JobDetails.objects.all()},context_instance=RequestContext(request))
    
@login_required
def upload_resume(request):
    currentuser = request.session.get('name1')
    if request.POST:
        try :
                candidateemail = request.POST.get('candidateemail')
                candidatename = request.POST.get('candidatename')
                skillname = request.POST.get('skillname')
                experience = request.POST.get('experience')
                visastatus = request.POST.get('visastatus')
                billrate = request.POST.get('billrate')
                availability = request.POST.get('availability')
                remarks = request.POST.get('remarks')
                #resume = request.POST.get('inputGroupFile01')
                recruiterobj = Recruiter.objects.get(username=currentuser)
                skillobj=TechnicalSkills.objects.get(primaryskill=skillname)
                Resume.objects.create(candidateemail=candidateemail,candidatename=candidatename,primaryskill=skillobj,resume=request.FILES['inputGroupFile01'],uploaddate=date.today(),resumestatus="submitted",submittedby=recruiterobj,experience=experience,visastatus=visastatus,billrate=billrate,availability=availability,remarks=remarks)
                return render_to_response('success.html',{'currentuser': currentuser,'userobject':Recruiter.objects.get(username=currentuser),'success': "Resume uploaded successfully"},
                                      context_instance=RequestContext(request))
        except Exception as error:
            return render_to_response('error.html',{'currentuser': currentuser,'userobject':Recruiter.objects.get(username=currentuser),'error': error},
                                      context_instance=RequestContext(request))
    return render_to_response ('uploadresume.html',{'currentuser': currentuser,'userobject':Recruiter.objects.get(username=currentuser),'obj':TechnicalSkills.objects.all()},context_instance=RequestContext(request))

@login_required    
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
                return render_to_response('success.html',{'currentuser': currentuser,'userobject':Recruiter.objects.get(username=currentuser),'success': "Interview scheduled for " + candidateemail},
                                      context_instance=RequestContext(request))
        except Exception as error:
            return render_to_response('error.html',{'currentuser': currentuser,'userobject':Recruiter.objects.get(username=currentuser),'error': error},
                                      context_instance=RequestContext(request))
    '''return render_to_response('uploadresume.html', {'currentuser': currentuser,
                                                    'obj': JobDetails.objects.filter(jobstatus='assigned').filter(
                                                        assignedto=currentuser).values('clientname').distinct(),
                                                    'obj1': JobDetails.objects.filter(jobstatus='assigned').filter(
                                                        assignedto=currentuser).values('positionname').distinct()},
                              context_instance=RequestContext(request))'''

    return render_to_response ('scheduleinterview.html',{'currentuser': currentuser,'userobject':Recruiter.objects.get(username=currentuser),'obj1':Recruiter.objects.get(username=currentuser),'obj2':Resume.objects.all(),'obj3':JobDetails.objects.all().filter(assignedto=currentuser)},context_instance=RequestContext(request))

@login_required
def search_resume(request):
    currentuser = request.session.get('name1')
    return render_to_response('searchresume.html', {'currentuser': currentuser, 'userobject':Recruiter.objects.get(username=currentuser),'obj': Resume.objects.all()},
                              context_instance=RequestContext(request))
                              
@login_required
def open_requirement(request):
    currentuser = request.session.get('name1')
    return render_to_response('openrequirement.html', {'currentuser': currentuser, 'userobject':Recruiter.objects.get(username=currentuser),'obj': JobDetails.objects.all().exclude(jobstatus='closed')},
                              context_instance=RequestContext(request))
                              
def save_book_form(request, form, template_name):    
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            books = JobDetails.objects.all().exclude(jobstatus='closed')
            data['html_book_list'] = render_to_string('partial_book_list.html', {
                'books': books
            })
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)

def book_update(request, jobid):
    book = get_object_or_404(JobDetails, pk=jobid)
    if request.method == 'POST':
        form = JobDetailsForm(request.POST, instance=book)
    else:
        form = JobDetailsForm(instance=book)
    return save_book_form(request, form, 'partial_book_update.html')   

def save_resume_form(request, form, template_name):    
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            books = Resume.objects.all()
            data['html_book_list'] = render_to_string('partial_resume_list.html', {
                'books': books
            })
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)

def resume_update(request, candidateemail):
    book = get_object_or_404(Resume, pk=candidateemail)
    if request.method == 'POST':
        form = ResumeDetailsForm(request.POST, instance=book)
    else:
        form = ResumeDetailsForm(instance=book)
    return save_resume_form(request, form, 'partial_resume_update.html')      
                              
@login_required
def generate_report(request):
    currentuser = request.session.get('name1')
    if request.POST:

        startdate = request.POST.get('startdate')
        enddate = request.POST.get('enddate')
        reporttype = request.POST.get('reporttype')
                
        cursor = connection.cursor()

        cursor.execute('''SELECT count("jobs_interview"."interviewstatus"), "jobs_interview"."interviewstatus","jobs_jobdetails"."vendorname_id", "jobs_jobdetails"."jobrole", "jobs_jobdetails"."jobstatus", "jobs_jobdetails"."jobcreatedate", "jobs_jobdetails"."assignedto" FROM "jobs_jobdetails" LEFT OUTER JOIN "jobs_interview" ON ("jobs_jobdetails"."jobid" = "jobs_interview"."jobid_id") WHERE "jobs_jobdetails"."jobcreatedate" >= (%s) AND "jobs_jobdetails"."jobcreatedate" <= (%s) GROUP BY "jobs_jobdetails"."vendorname_id", "jobs_jobdetails"."jobrole","jobs_interview"."interviewstatus"''',(datetime.strptime(startdate, '%m/%d/%Y').strftime('%Y-%m-%d'),datetime.strptime(enddate, '%m/%d/%Y').strftime('%Y-%m-%d')))
        rows = cursor.fetchall()

        final_dict1={}

        bdm_dict={}
        #print rows
        report1 = []
        if len(rows) != 0:

            for item in rows:
                    key = (item[2],item[3],item[4])
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
            final_list = []
            for key,values in final_dict1.items():
                final_list.append([key[0],key[1],key[2],values[0],values[1],values[2],values[3],values[4],values[5]])

            columnnames = ['client','jobrole','jobstatus','assign','date','source','screen','select','reject']
            df = pd.DataFrame.from_dict(final_list)
            df.columns = columnnames
            df['date'] = pd.to_datetime(df['date'])
            df.set_index(df["date"],inplace=True)

            df1=df.groupby(['client','jobrole','assign','jobstatus']).resample('D').sum()
            if reporttype == 'daily':
                df2=df.groupby(['assign','jobstatus']).resample('D').sum()
            elif reporttype == 'weekly':
                df2=df.groupby(['assign','jobstatus']).resample('W').sum()
            elif reporttype == 'monthly':
                df2=df.groupby(['assign','jobstatus']).resample('M').sum()


            for name in df1.index:         
                list1 = [name[0],name[1], name[2], name[3], name[4],df1.loc[name].values[0],df1.loc[name].values[1],df1.loc[name].values[2],df1.loc[name].values[3]]
                report1.append(list1) 

            
        return render_to_response('generatereport.html', {'currentuser': currentuser, 'userobject':Recruiter.objects.get(username=currentuser),'objdict':report1},
                                  context_instance=RequestContext(request))    
    return render_to_response('selectdate.html', {'currentuser': currentuser,'userobject':Recruiter.objects.get(username=currentuser)},
                                  context_instance=RequestContext(request))        
