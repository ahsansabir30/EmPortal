from django.contrib import admin
from .models import Department, JobRole, Employee, User, Timesheet, AnnualLeave, SickLeave, Room, Messages, Project, ProjectStage, EmployeeAltContact

admin.site.register(Department)
admin.site.register(Employee)
admin.site.register(User)
admin.site.register(JobRole)
admin.site.register(Timesheet)
admin.site.register(AnnualLeave)
admin.site.register(SickLeave)
admin.site.register(Room)
admin.site.register(Messages)
admin.site.register(Project)
admin.site.register(ProjectStage)
admin.site.register(EmployeeAltContact)