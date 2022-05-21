from email import message
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from .models import Department, Employee, JobRole, User, Timesheet, AnnualLeave, SickLeave, Room, Messages, Project, ProjectStage, EmployeeAltContact
from .forms import DepartmentForm, EmployeeForm, JobRoleForm, UserForm, SickLeaveForm, TimeSheetForm, RoomForm, ProjectForm, ProjectStageForm, EmployeeAltContactForm
from datetime import date, datetime, timezone, timedelta
from .decorators import admin_only
from django.contrib.auth.decorators import user_passes_test

def Access(request):
    return render(request, 'base/access.html')

def LoginUser(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == "POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'Username does not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Username and Password do not exist')

    context={'page': page}
    return render(request, 'base/login.html', context)


@login_required(login_url='login')
def LogoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
@admin_only
def CreateUser(request):
    page = " "
    message = " "
    form = UserForm()
    # checking for user where employee profile was incomplete (if not should ask user to delete the given user or to complete given user profile) 
    user = User.objects.filter().latest('id')
    try:
        # user and employee profile exist - so allow new-user creation
        name = Employee.objects.get(username=user)
        name = True
    except: 
        # user name exist, however employee profile does not - so either complete employee profile or delete user
        name = False

    if name == False:
        message = f"Complete user profile: {user}, before you creating a new user"
        page = 'finish profile'  

    if name == True:
        if request.method == 'POST':
            form = UserForm(request.POST)
            if form.is_valid():
                # checking if the user is gonna be an admin or an employee
                display_type = request.POST["display_type"]
                user = form.save(commit=False)
                user.username = user.username.lower()
                user.save()
                # onece the user has been saved, we can allocate user a group (so between an employee or an admin) 
                group = Group.objects.get(name=str(display_type))
                user.groups.add(group)
                user.save()
                return redirect ('create-employee')
            else:
                messages.error(request, 'An error occured during registration')


    context = {'form': form, 'message': message, 'user': user, 'page':page}
    return render(request, 'base/userprofile_form.html', context)

@login_required(login_url='login')
@admin_only
def CreateEmployeeProfile(request): 
    page = 'create_employee'
    form = EmployeeForm()
    user = User.objects.filter().latest('id')
    print(user)
    try:
        name = Employee.objects.get(username=user)
        name = True
    except: 
        name = False

    if name == True:
        # need to create a new user before creating an employee profile
        page = 'create user'
    elif name == False:
        # if a user exist without an employee profile, told to finish profile first 
        if request.method == 'POST':
            form = EmployeeForm(request.POST)
            if form.is_valid():
                employee = form.save(commit=False)
                employee.username = user
                employee.save()
                form.save()
                return redirect('dashboard') 

    context = {'form': form, 'page':page}
    return render(request, 'base/userprofile_form.html', context)

@login_required(login_url='login')
@admin_only
def DeleteUser(request, pk):
    user = User.objects.get(id=pk)

    if request.method == 'POST':
        user.delete()
        return redirect('dashboard')

    context = {'obj': user}
    return render(request, 'base/delete.html', context)

@login_required(login_url='login')
def Dashboard(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    employees = Employee.objects.filter(
        Q(first_name__icontains=q) | 
        Q(last_name__icontains=q) |
        Q(department__department__icontains=q) 
        )

    employee_name = request.user
    employee_count = employees.count()    

    context = {'employees': employees, 'employee_count': employee_count, 'employee_name': employee_name}
    return render(request, 'base/dashboard.html', context)

# currently only an employee can edit his/her details - need to make it so only a super user can edit an employee profile
@login_required(login_url='login')
@admin_only
def UpdateEmployee(request, pk):
    employee = Employee.objects.get(id=pk)
    form = EmployeeForm(instance=employee)

    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            info = form.save(commit = False)
            info.username = employee.username
            info.save()
            form.save()
            return redirect('dashboard')

    context = {'form': form}
    return render(request, 'base/userprofile_form.html', context)

@login_required(login_url='login')
@admin_only
def DeleteEmployee(request, pk):
    employee = Employee.objects.get(id=pk)

    if request.method == 'POST':
        employee.delete()
        return redirect('dashboard')

    context = {'obj': employee}
    return render(request, 'base/delete.html', context)

@login_required(login_url='login')
def EmployeeProfile(request, pk):
    employee = Employee.objects.get(id=pk)
    try:
        employee_alt = EmployeeAltContact.objects.get(id=employee.id)
    except:
        employee_alt = None

    context = {'employee': employee, 'employee_alt':employee_alt}
    return render(request, 'base/employee.html', context)

@login_required(login_url='login')
@admin_only
def CreateEmployeeAlt(request, pk):
    form = EmployeeAltContactForm()
    
    # checking if the user already has an alt profile - if so redirect to employee page
    try:
        check = EmployeeAltContact.objects.get(id=pk)
        return redirect('/employee/' + str(pk))       
    except:
        check = True

    if check == True:
        if request.method == 'POST':
            form = EmployeeAltContactForm(request.POST)
            if form.is_valid():
                employee = form.save(commit=False)
                employee.username = request.user
                employee.save()
                form.save()
                return redirect('/employee/' + str(request.user.id))

    context = {'form': form, 'message': message}
    return render(request, 'base/employeeplus.html', context)

@login_required(login_url='login')
@admin_only
def UpdateEmployeeAlt(request, pk):
    employee = Employee.objects.get(id=pk)
    section = " "
    form = " "
    # checking if user alt profile exist - if not do nothing
    try:
        section = "update"
        alt = EmployeeAltContact.objects.get(id=pk)
        form = EmployeeAltContactForm(instance=alt)
        if request.method == 'POST':
            form = EmployeeAltContactForm(request.POST, instance=alt)
            if form.is_valid():
                instance = form.save(commit = False)
                instance.username = alt.username
                instance.save()
                form.save()
                return redirect('/employee/' + str(employee.id))
    except:
        section = "User alt profile does not exist, so please create profile first before updating"
        form = EmployeeAltContactForm
        if request.method == 'POST':
            form = EmployeeAltContactForm(request.POST)
            if form.is_valid():
                instance = form.save(commit = False)
                instance.username = employee.username
                instance.save()
                form.save()
                return redirect ('/employee/' + str(employee.id))
        
    context = {'form': form, 'section':section}
    return render(request, 'base/employeeplus.html', context)

########## DEPARTMENT ##############
@login_required(login_url='login')
def Departments(request):
    page = 'department'
    department_form = DepartmentForm
    if request.method == 'POST':
        department_form = DepartmentForm(request.POST)
        if department_form.is_valid():
            department_form.save()
            return redirect ('departments')

    q = request.GET.get('q') if request.GET.get('q') != None else ''

    department = Department.objects.filter(
        Q(department__icontains=q)
    )

    context = {'department_form': department_form, 'page': page, 'department': department}
    return render(request, 'base/department.html', context)

@login_required(login_url='login')
@admin_only
def UpdateDepartment(request, department):
    department = Department.objects.get(department=department)
    department_form = DepartmentForm(instance=department)

    if request.method == 'POST':
        department_form = DepartmentForm(request.POST, instance=department)
        if department_form.is_valid():
            department_form.save()
            return redirect('departments')

    q = request.GET.get('q') if request.GET.get('q') != None else ''

    department = Department.objects.filter(
        Q(department__icontains=q)
    )

    context = {'department_form': department_form, 'department': department}
    return render(request, 'base/department.html', context)

@login_required(login_url='login')
@admin_only
def DeleteDepartment(request, department):
    department = Department.objects.get(department=department)

    if request.method == 'POST':
        department.delete()
        return redirect('departments')

    context = {'obj': department}
    return render(request, 'base/delete.html', context)

########## JOB ROLE ##############
@login_required(login_url='login')
def JobRoles(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    job_role = JobRole.objects.filter(
        Q(department__department__icontains=q) |
        Q(job_role__icontains=q)
    )
    
    context = {'job_role': job_role}
    return render(request, 'base/job_roles.html', context)

@login_required(login_url='login')
@admin_only
def CreateJobRole(request):
    page = 'role_form'
    job_form = JobRoleForm

    if request.method == 'POST':
        job_form = JobRoleForm(request.POST)
        if job_form.is_valid():
            job_form.save()
            return redirect ('job-roles')
        else:
            messages.error(request, 'An error occured whilst adding Job Role')

    context = {'job_form': job_form, 'page':page}
    return render(request, 'base/job_roles.html', context)

@login_required(login_url='login')
@admin_only
def UpdateJobRole(request, pk):
    page = 'role_form'
    job_role = JobRole.objects.get(id=pk)
    job_form = JobRoleForm(instance=job_role)

    if request.method == 'POST':
        job_form = JobRoleForm(request.POST, instance=job_role)
        if job_form.is_valid():
            job_form.save()
            return redirect('job-roles')

    context = {'job_form': job_form, 'page': page}
    return render(request, 'base/job_roles.html', context)

@login_required(login_url='login')
@admin_only
def DeleteJobRole(request, pk):
    role = JobRole.objects.get(id=pk)

    if request.method == 'POST':
        role.delete()
        return redirect('job-roles')

    context = {'obj': role,}
    return render(request, 'base/delete.html', context)
########## TIME ##############
@login_required(login_url='login')
def TimeSheet(request, pk):
    user = User.objects.get(id= pk)
    message = " "

    clock_action = request.POST.get('clock_action', '')
    try:
        if clock_action == "ClockIn":
            logged_status = Timesheet.objects.filter(username=user).latest('clocked_in')
            if logged_status.clocked_out != None:
                now = datetime.now(timezone.utc)
                timesheet = Timesheet(username=user, clocked_in= now, recorded_by=user)
                timesheet.save()
            else:
                message = "Please, can you clock out first"

        elif clock_action == "ClockOut":
            logged_status = Timesheet.objects.filter(username=user).latest('clocked_in')
            if logged_status.clocked_out == None:
                now = datetime.now(timezone.utc)
                logged_status.clocked_out = now
                logged_status.save()
            else:
                message = "Please, can you clock in first"
    except:
        now = datetime.now(timezone.utc)
        timesheet = Timesheet(username= user, clocked_in= now, recorded_by= user)
        timesheet.save()
        message = "You have clocked in"

    q = request.GET.get('q') if request.GET.get('q') != None else ''


    employee_time = Timesheet.objects.filter(
        Q(clocked_in__icontains=q) |
        Q(clocked_out__icontains=q) |
        Q(recorded_by__username__icontains = q)
    ).filter(username__username = user.username)

    context = {'employee_time': employee_time, 'message': message,}
    return render(request, 'base/timesheet.html', context) 

@login_required(login_url='login')
@admin_only
def AllTimeSheet(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    employee_time = Timesheet.objects.filter(
        Q(clocked_in__icontains=q) |
        Q(clocked_out__icontains=q) |
        Q(username__username__icontains = q) |
        Q(recorded_by__username__icontains = q)
    )

    context = {'employee_time': employee_time}
    return render(request, 'base/timesheet_manager.html', context)

@login_required(login_url='login')
@admin_only
def EditTimeSheet(request, pk):
    page = 'Edit Timesheet'
    time = Timesheet.objects.get(id=pk)
    timesheet_form = TimeSheetForm(instance=time)

    if request.method == 'POST':
        timesheet_form = TimeSheetForm(request.POST, instance=time)
        if timesheet_form.is_valid():
            timesheet_form.recorded_by = request.user
            timesheet_form.save()
            return redirect('manager-access-timesheet')

    context = {'timesheet_form': timesheet_form, 'page': page}
    return render(request, 'base/timesheet.html', context)

@login_required(login_url='login')
@admin_only
def DeleteTimeSheet(request, pk):
    time = Timesheet.objects.get(id=pk)
   
    if request.method == 'POST':
        time.delete()
        return redirect('manager-access-timesheet')

    context = {'obj': time}
    return render(request, 'base/delete.html', context)   

@login_required(login_url='login')
def AddAnnualLeave(request, pk):
    user = User.objects.get(id= pk)

    message= ""
    date_from = request.POST.get('date_from', '')
    date_to = request.POST.get('date_to', '')
    user_message = request.POST.get('user_message', '')
    
    if date_from > date_to:
        message = "Incorrect Format"
    else:
        submit_leave = request.POST.get('submit_leave', '')
        if submit_leave == "submit":
            leave = AnnualLeave(username= user, recorded_by= user, status=1, date_from=date_from, date_to=date_to, comments=user_message)
            leave.save()
            message = "Your annual leave has been submitted"

    q = request.GET.get('q') if request.GET.get('q') != None else ''

    annual_leave = AnnualLeave.objects.filter(
        Q(recorded_datetime__icontains=q) |
        Q(date_from__icontains=q) |
        Q(date_to__icontains = q) |
        Q(recorded_by__username__icontains = q)
    ).filter(username__username = user.username)

    context = {'user': user, 'annual_leave': annual_leave, 'message': message,}
    return render(request, 'base/timesheet_leave.html', context)

@login_required(login_url='login')
def CancelAnnualLeave(request, pk):
    page = 'cancel_leave'
    cancel_leave = AnnualLeave.objects.get(id= pk)

    user_pk = request.user.id

    if request.method == 'POST':
        cancel_leave.status= 4
        cancel_leave.save()
        return redirect('/annual-leave/'+ str(user_pk))

    context = {'page':page}
    return render(request, 'base/delete.html', context)

@login_required(login_url='login')
@admin_only
def ManagerAnnualLeave(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    leave_request = AnnualLeave.objects.filter(
        Q(username__username__icontains=q) |
        Q(recorded_datetime__icontains=q) |
        Q(date_from__icontains=q) |
        Q(date_to__icontains = q) |
        Q(recorded_by__username__icontains = q)
    )

    context = {'leave_request': leave_request,}

    return render(request, 'base/timesheet_mleave.html', context)

@login_required(login_url='login')
@admin_only
def ManagerAnnualLeaveAction(request, action, holiday_request_id):
    page = 'ManagerAnnualLeave'

    if action == "approve":
        annual_leave = AnnualLeave.objects.get(id= holiday_request_id)
        annual_leave.status = 2
        annual_leave.save()
        return redirect(request.META.get('HTTP_REFERER'))

    if action == "reject":
        annual_leave = AnnualLeave.objects.get(id= holiday_request_id)
        annual_leave.status = 3
        annual_leave.save()
        return redirect(request.META.get('HTTP_REFERER'))

    context = {'page': page}
    return render(request, 'base/timesheet_leave.html', context)

# returns the date between 2 dates
def date_range_list(start_date, end_date):
    # Return list of datetime.date objects between start_date and end_date (inclusive).
    date_list = []
    curr_date = start_date
    while curr_date <= end_date:
        date_list.append(curr_date)
        curr_date += timedelta(days=1)
    return date_list

@login_required(login_url='login')
@admin_only
def SickLeaveView(request):
    page = 'Sick Leave'

    sick_form = SickLeaveForm()
    if request.method == 'POST':
        sick_form = SickLeaveForm(request.POST)
        if sick_form.is_valid():
            form = sick_form.save(commit=False)
            form.recorded_by = request.user
            form.save()

            return redirect ('sick-leave')
        else:
            messages.error(request, 'An error occured whilst adding SICK LEAVE')
    

    sick_leave = SickLeave.objects.values('username', 'date_from', 'date_to')
    now = date.today()

    sick_counter = 0
    for dates in sick_leave:
        date_from = dates['date_from']
        date_to = dates['date_to']
        if date_from == date_to:
            if date_from == now:
                sick_counter += 1
        else:    
            date_list = (date_range_list(date_from, date_to))
            for dates in date_list:
                if now == dates:
                    sick_counter += 1

    sick_leave = SickLeave.objects.all()
    

    context={'page': page, 'sick_form': sick_form, 'sick_leave': sick_leave, 'sick_counter': sick_counter}
    return render(request, 'base/timesheet_sickleave.html', context)

############# TEAMS ###################
@login_required(login_url='login')
def Rooms(request):
    room_user = Room.objects.filter(participants=request.user)
    
    recent_room = Room.objects.filter(participants=request.user).only('id').all()
    recent_activity = Messages.objects.filter(room__in=recent_room)

    context = {'rooms': room_user, 'recent_activity': recent_activity}
    return render(request, 'base/room.html', context)


@login_required(login_url='login')
def CreateRoom(request):
    form = RoomForm()
   
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room_name = form.cleaned_data.get('room')
            description = form.cleaned_data.get('description')
            participants = form.cleaned_data.get('participants')

            instance = Room.objects.create(
                host=request.user,
                room=room_name,
                description=description
            )
            
            for user in participants:
                instance.participants.add(user)
        

            return redirect('rooms')

    context = {'form': form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def UpdateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.method == 'POST':
        room.room = request.POST.get('room')
        room.description = request.POST.get('description')

        # clearing existing participants            
        room.participants.clear()
        # getting the new participants of the room/ and adding them to 'room' 
        participants = request.POST.getlist('participants')
    
        for user in participants:
            room.participants.add(user)
    
        room.save()
        return redirect('rooms')

    context = {'form': form}
    return render(request, 'base/room_form.html', context)    

@login_required(login_url='login')
def DeleteRoom(request, pk):
    room = Room.objects.get(id=pk)
   
    if request.method == 'POST':
        room.delete()
        return redirect('rooms')

    context = {'obj': room}
    return render(request, 'base/delete.html', context)   

@login_required(login_url='login')
def ViewRoom(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.messages_set.all()
    participants = room.participants.all()

    # view room is only accessible if you are a participant of a chat room
    participant = room.participants.all()
    if request.user not in participant:
        return redirect('access')
    
    if request.method == 'POST':
        message = Messages.objects.create(
            user=request.user,
            room=room,
            text=request.POST.get('text')
        )
        room.participants.add(request.user)
        return redirect('view-room', pk=room.id)

    rooms = Room.objects.filter(participants=request.user)    

    context = {'room': room, 'room_messages': room_messages, 'participants': participants, 'rooms': rooms}
    return render(request, 'base/room_view.html', context)

@login_required(login_url='login')
def DeleteMessage(request, pk):
    message = Messages.objects.get(id=pk)
   
    if request.user != message.user:
        return HttpResponse('Your not allowed here')

    if request.method == 'POST':
        message.delete()
        return redirect('rooms')

    context = {'obj': message}
    return render(request, 'base/delete.html', context)   

############# Projects ###################
@login_required(login_url='login')
def ViewProjects(request):
    projects = Project.objects.filter(participants=request.user)

    user_project = Project.objects.filter(participants=request.user).only('id').all()
    stages = ProjectStage.objects.filter(project__in=user_project).order_by('-updated', '-created')

    current_datetime= datetime.now(timezone.utc)

    context = {'projects': projects, 'stages': stages, 'current_datetime': current_datetime}

    return render(request, 'base/projects.html', context)

@login_required(login_url='login')
def CreateProject(request):
    form = ProjectForm
    
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.host = request.user
            instance.save()
            form.save()
            return redirect('projects')
            
    context = {'form': form}

    return render(request, 'base/project_form.html', context)

@login_required(login_url='login')
def UpdateProject(request, pk):
    page ="update_project"
    project = Project.objects.get(id=pk)

    form = ProjectForm(instance=project)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('projects')

    context = {'form': form, 'page': page,}

    return render(request, 'base/project_form.html', context)

@login_required(login_url='login')
def DeleteProject(request, pk):
    project = Project.objects.get(id=pk)

    if request.method == 'POST':
        project.delete()
        return redirect('projects')

    context = {'obj': project}
    return render(request, 'base/delete.html', context)   

@login_required(login_url='login')
def ViewProjectStages(request, pk):
    message = " "
    project = Project.objects.filter(id=pk).only('id').all()
    project_stages = ProjectStage.objects.filter(project__in=project).order_by('stages')

    # need to check if the project has any stages = if no stages are found the code below thus not need to run (as it is correlated to project stages)
    if len(project_stages) != 0:
        # if all stages are complete, we change the status of the project in question as complete
        # to do this we need to check if all stages of the project in question are complete 
        stage_status = ProjectStage.objects.filter(project__in=project).filter(status="False")
        # if there is stage which has the the status 'false', the project is not complete and this will be passed into the project status 
        if len(stage_status) > 0:
            project_status = False
            Project.objects.filter(id=pk).update(status=False)
        # if there is no stage status as false, the project is complete and this will be reflected on project view page (as green)
        else:
            Project.objects.filter(id=pk).update(status=True)
   
    # counting all stages
    ps_count = project_stages.count()    

    project_name = Project.objects.filter(id=pk).all()[0]
    project_date = Project.objects.filter(id=pk).values('date_from','due_date',)
    date_from = project_date[0]['date_from']
    date_to = project_date[0]['due_date']

    form = ProjectStageForm
    if request.method == 'POST':
        form = ProjectStageForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            # saving stage under the project it was created in
            instance.project = project_name
            # check if the data_to is greater than date_from
            if instance.date_to < instance.date_from:
                message = f"Failed to add stage {instance.stage_name}, due date has to be greater than date from"
            else:
                # checking if the dates for the new project stage are in between dates under the project  
                if date_from <= instance.date_from <= instance.date_to <= date_to:
                    message = f"Successfully added project stage {instance.stage_name}"
                    instance.save()
                    form.save()
                    return redirect('/view-stage/' + str(pk))
                else:
                    # if this has failed, this will be rendered in the html 
                    message = "Dates are not between the dates for this project, please reconsider"  

    current_datetime= datetime.now(timezone.utc)

    context = {'project_stages': project_stages, 'project_name': project_name, 'form': form, 'message': message, 
    'date_from': date_from, 'date_to': date_to, 'date_from': date_from, 'ps_count':ps_count, 'current_datetime': current_datetime}

    return render(request, 'base/project_stages.html', context)

@login_required(login_url='login')
def UpdateProjectStage(request, pk):
    page = "form"
    project_stage = ProjectStage.objects.get(id=pk)
    form = ProjectStageForm(instance=project_stage)
    
    project_id = project_stage.project.id

    if request.method == 'POST':
        form = ProjectStageForm(request.POST, instance=project_stage)
        if form.is_valid():
            form.save()
            return redirect('/view-stage/' + str(project_id))

    context = {'form': form, 'page': page}

    return render(request, 'base/project_form.html', context)

@login_required(login_url='login')
def DeleteProjectStage(request, pk):
    stage = ProjectStage.objects.get(id=pk)
   
    if request.method == 'POST':
        stage.delete()
        return redirect('/view-stage/' + str(stage.project.id))

    context = {'obj': stage}
    return render(request, 'base/delete.html', context)   


############# Analysis ###################
@login_required(login_url='login')
def AnalyseView(request):

    employees = Employee.objects.all()
    employee_count = employees.count()


    department = Department.objects.all().order_by('department')
    department_count = department.count()

    dep = []
    data = []

    for x in department:
        dep.append(x)
        count = Employee.objects.filter(department__department__contains=x).count()
        data.append(count)
    
    project = Project.objects.all().order_by('project')
    project_count = project.count()

    proj = []
    datap = []

    for x in project:
        proj.append(x)
        count = ProjectStage.objects.filter(project__project__contains=x).count()
        datap.append(count)

    room = Room.objects.all()
    room_count = room.count()

    context = {'employees': employees, 'employee_count': employee_count, 
                'department': department, 'department_count':department_count,
                'project': project, 'project_count': project_count,'room': room, 
                'room_count': room_count, 'dep': dep, 'data': data, 'proj':proj,
                'datap': datap}
    return render(request, 'base/analyse.html', context)  