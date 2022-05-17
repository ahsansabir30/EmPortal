from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from datetime import datetime, timezone


class User(AbstractUser):
    username = models.CharField(max_length = 100, unique=True, null=False)

    def __str__(self):
        return self.username


class Department(models.Model):
    department = models.CharField(max_length=100, null=True, unique=True)   
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.department

class JobRole(models.Model):
    department = models.ForeignKey(Department, null=True, on_delete= models.SET_NULL)
    job_role = models.CharField(max_length=150, null=True, unique=True)

    def __str__(self):
        return self.job_role

class Employee(models.Model):
    avatar = models.ImageField(null=True, default="user-clear.png")
    username = models.OneToOneField(User, on_delete= models.CASCADE)
    TITLE_CHOICE = (('Mr', 'Mr'), ('Ms', 'Ms'), ('Mrs', 'Mrs'), ('Miss', 'Miss'), ('Dr', 'Dr'), ('Sir','Sir'), ('Other', 'Other'))
    title = models.CharField(max_length=5, choices=TITLE_CHOICE)
    GENDER_CHOICE = (
        ('M','Male'), 
        ('F', 'Female'),
        ('O', 'Other')
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICE)
    email = models.EmailField(max_length=200, unique= True, null=True)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank =True, null=True)
    last_name = models.CharField(max_length = 50) 
    phoneNumber = models.CharField(max_length=20)
    address = models.CharField(max_length=200)
    postcode = models.CharField(max_length=7)
    city = models.CharField(max_length=100)
    nationality = models.CharField(max_length=20)
    dateofbirth = models.DateField(max_length=8)
    join_date = models.DateField(blank =True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, blank=True, null=True)
    job_role = models.ForeignKey(JobRole, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return str(self.username)

class EmployeeAltContact(models.Model):
    username = models.OneToOneField(User, unique=True, on_delete=models.CASCADE)
    other_email = models.EmailField(max_length=200, blank=True, null=True)
    other_phone = models.CharField(max_length=20, blank=True, null=True)
    github = models.CharField(max_length=100, blank=True, null=True)
    website = models.CharField(max_length=200, blank=True, null=True)
    profile = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.username)
# Time
class Timesheet(models.Model):
    username = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE, related_name="timesheet_username")
    recorded_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="recorded_username")
    # when user clocks in - it will create a record for the employee, and will date stamp the time clocked_in 
    clocked_in = models.DateTimeField()
    # when user clocks out - it will update clocked out with the new time 
    clocked_out = models.DateTimeField(blank=True, null=True)
    hours_worked = models.DateTimeField(null=True, blank=True)
    comments = models.TextField(blank=True, null=True )

    def hours_worked(self):
        if self.clocked_out == None:
            date_time = datetime.now(timezone.utc)
            return date_time - self.clocked_in
        else:
            return self.clocked_out - self.clocked_in

    def __str__(self):
        return "%s -- %s -- %s" % (self.username, self.clocked_in, self.clocked_out)

    
    class Meta:
        ordering = ['-recorded_by']

class AnnualLeave(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE, related_name="annual_leave_username")
    recorded_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="annual_leave_recorded_by")   
    recorded_datetime = models.DateTimeField(auto_now_add=True)
    status_choices = ((1,'Pending'), (2, 'Granted'), (3, 'Rejected'), (4, 'Cancelled'),)
    status = models.IntegerField(choices=status_choices)
    date_from = models.DateField()
    date_to = models.DateField()
    comments = models.TextField(max_length=500, blank=True, null=True)

    def __str__(self):
        return "%s -- %s -- %s -- %s" % (self.username, self.date_from, self.date_to, self.status)

    class Meta:
        ordering = ['-recorded_datetime']

class SickLeave(models.Model):
    username  = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sick_leave_username")
    recorded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recorded_by_username")   
    recorded_datetime = models.DateTimeField(auto_now_add=True)
    date_from = models.DateField()
    date_to = models.DateField()
    doctors_note = models.BooleanField()
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.username)

# Team
class Room(models.Model):
    host = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    room = models.CharField(max_length=500, unique=True)
    description = models.TextField(null=True, blank=True)
    participants = models.ManyToManyField(User, related_name="room_participants")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.room)     


    def __unicode__(self):
        return self.participants 

class Messages(models.Model):
    room = models.ForeignKey(Room, null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    text = models.TextField(null=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text[0:100]       

class Project(models.Model):
    project = models.CharField(max_length=100, unique=True)
    host = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    participants = models.ManyToManyField(User, related_name="project_participants")
    created = models.DateField(auto_now_add=True)
    date_from = models.DateTimeField()
    due_date = models.DateTimeField()
    status = models.BooleanField()  

    class Meta:
       ordering = ['-created']

    def __str__(self):
        return str(self.project)    

class ProjectStage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    stage_name = models.CharField(max_length = 200)
    stages = models.IntegerField()
    description = models.TextField(null=True, blank=True)
    date_from = models.DateTimeField()
    date_to = models.DateTimeField()
    status = models.BooleanField()  
    created = models.DateTimeField(auto_now_add=True)  
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-stages']

    def __str__(self):
        return str(self.status)