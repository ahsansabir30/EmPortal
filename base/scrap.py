def TimeSheet(request):
    employee_id = request.user.id
    # username = request.user
    username = Employee.objects.get(id = employee_id)
    form = TimeSheetForm(instance=username)

    if request.method == 'POST':
        # remove instance - allows it to work (only if you include the username in the form)
        form = TimeSheetForm(request.POST)
        if form.is_valid():
            username = form.save(commit=False)
            username = request.user
            username.save()
            form.save()

    employee_time = Timesheet.objects.all()

    context = {'form': form, 'employee_time': employee_time, 'username':username}
    return render(request, 'base/timesheet.html', context)

def TimeSheet2(request):
    employee_id = request.user.id
    username = Employee.objects.get(id = employee_id)
    form = TimeSheetForm2(instance=username)

    if request.user != username.username:
        return redirect('access')

    if request.method == 'POST':
        # remove instance - allows it to work
        form = TimeSheetForm2(request.POST)
        if form.is_valid():
            username = form.save(commit=False)
            username = request.user 
            username.save()
            form.save()

    #employee_time = Timesheet2.objects.all()

    context = {'form': form}
    return render(request, 'base/timesheet2.html', context)

############ Timesheet ##########################
# model.py
class Timesheet(models.Model):
    username = models.ForeignKey(User, null=False, on_delete= models.CASCADE, related_name="employee_username")
    recorded_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="recorded_by")   
    # recorded_datetime = models.DateTimeField(auto_now_add=True)
    clocking_time = models.DateTimeField(auto_now_add=True)
    # whether the user has clocked in or out
    LOGGING_CHOICES = (
        ('IN', 'CLOCK-IN'),
        ('OUT', 'CLOCK-OUT')
    )
    logging = models.CharField(max_length=3, choices=LOGGING_CHOICES)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-recorded_by']

    def __str__(self):
        return "%s checked %s at %s " % (self.username, self.logging, self.clocking_time)

# view.py
def TimeSheet(request):
    employee_id = request.user.id
    employee = Employee.objects.get(id = employee_id)

    clock_action = request.POST.get('clock_action', '')
    message = ""
    try:
        logged_status = Timesheet.objects.filter(username = employee.username).latest('clocking_time')
        if clock_action == "ClockIn":
            if logged_status.logging == "OUT":
                timesheet = Timesheet(username=employee.username, recorded_by=employee.username, logging="IN", comments= NULL)
                timesheet.save()
                message = "You have clocked in"
            else:
                message = "You need to clock out, first"
        elif clock_action == "ClockOut":
            if logged_status.logging == "IN":
                timesheet = Timesheet(username=employee.username, recorded_by=employee.username, logging="OUT", comments= NULL)
                timesheet.save()
                message = "You have clocked out"
            else:
                message = "You need to clock in, first"
    except:
        logged_status = "New"
        if clock_action == "ClockIn":
            if logged_status == "New":
                timesheet = Timesheet(username=employee.username, recorded_by=employee.username, logging="IN", comments= NULL)
                timesheet.save()
                "You have clocked in"

    employee_time = Timesheet.objects.all()

    context = {'message': message, 'employee_time': employee_time}

    return render(request, 'base/timesheet.html', context)


"""
@login_required(login_url='login')
def TimeSheet(request, pk):
    user = User.objects.get(id= pk)
    message = " "

    # checking if user is a new user
    clock_action = request.POST.get('clock_action', '')
    if clock_action == "ClockIn" or clock_action == "ClockOut":
        status = Timesheet.objects.filter(username=user)
        if status:
            print("old user")
            if clock_action == "ClockIn":
                logged_status = Timesheet.objects.filter(username=user).latest('clocked_in')
                if logged_status.clocked_out != None:
                    now = datetime.now(timezone.utc)
                    timesheet = Timesheet(username=user, clocked_in= now, recorded_by=user, comments=NULL)
                    #timesheet = Timesheet(username=user, recorded_by=user, comments=NULL)
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
        else:
            print("new user")
            now = datetime.now(timezone.utc)
            timesheet = Timesheet(username= user, clocked_in= now, recorded_by= user, comments= NULL)
            timesheet.save()
            message = "You have clocked in"

    q = request.GET.get('q') if request.GET.get('q') != None else ''


    employee_time = Timesheet.objects.filter(
        Q(clocked_in__icontains=q) |
        Q(clocked_out__icontains=q) |
        Q(username__username__icontains = q) |
        Q(recorded_by__username__icontains = q)
    )

    context = {'employee_time': employee_time, 'message': message}
    return render(request, 'base/timesheet.html', context) """


# need to add a search function for message
q = request.GET.get('q') if request.GET.get('q') != None else ''

    rooms = Room.objects.filter(
        Q(room__icontains=q) |
        Q(host__username__icontains=q) | 
        Q(description__icontains=q) 
        )   
