from django.urls import path, include
from . import views

urlpatterns = [
    # creation/login
    path('', views.LoginUser, name="login"),
    path('logout/', views.LogoutUser, name="logout"),
    path('create-user/', views.CreateUser, name="create-user"),
    path('delete-user/<str:pk>/', views.DeleteUser, name="delete-user"),

    # dashboard
    path('dashboard/', views.Dashboard, name="dashboard"),
    path('create-employee/', views.CreateEmployeeProfile, name="create-employee"),
    path('update-employee/<str:pk>/', views.UpdateEmployee, name="update-employee"),
    path('delete-employee/<str:pk>/', views.DeleteEmployee, name="delete-employee"),

    # additional employee information
    path('employee/<str:pk>/', views.EmployeeProfile, name="employee"),
    path('addon-employee/c=<str:pk>/', views.CreateEmployeeAlt, name="employee-alt"),
    path('addon-employee/u=<str:pk>/', views.UpdateEmployeeAlt, name="update-employee-alt"),
    # departments
    path('department/', views.Departments, name="departments"),
    path('delete-department/<str:department>/', views.DeleteDepartment, name="delete-department"),
    path('update-department/<str:department>/', views.UpdateDepartment, name="update-department"),

    # job-role
    path('job-roles/', views.JobRoles, name="job-roles"),
     path('create=job-roles/', views.CreateJobRole, name="create-role"),
    path('delete=job-roles/<str:pk>/', views.DeleteJobRole, name="delete-role"),
    path('update=job-roles/<str:pk>/', views.UpdateJobRole, name="update-role"),

    # time/ timesheet/ annual-leave/ sick-leave
    path('timesheet/<str:pk>/', views.TimeSheet, name="employee-timesheet"),
    path('manager/timesheet/', views.AllTimeSheet, name="manager-access-timesheet"),
    path('edit/timesheet/<str:pk>', views.EditTimeSheet, name="edit-timesheet"),
    path('delete/timesheet/<str:pk>', views.DeleteTimeSheet, name="delete-timesheet"),
    
    path('annual-leave/<str:pk>/', views.AddAnnualLeave, name="annual-leave"),
    path('cancel-annual-leave/<str:pk>/', views.CancelAnnualLeave, name="cancel-annual-leave"),
    path('manager-annual-leave/', views.ManagerAnnualLeave, name="manager-annual-leave"),
    path('holiday_request/<str:action>/<str:holiday_request_id>', views.ManagerAnnualLeaveAction, name="manager-holiday-request"),
    path('sick-leave/', views.SickLeaveView, name="sick-leave"),

    # teams
    path('rooms/', views.Rooms, name="rooms"),
    path('create-rooms/', views.CreateRoom, name="create-room"),
    path('room/<str:pk>/', views.ViewRoom, name="view-room"),
    path('update-rooms/<str:pk>/', views.UpdateRoom, name="update-room"),
    path('delete-rooms/<str:pk>/', views.DeleteRoom, name="delete-room"),
    path('delete-message/<str:pk>/', views.DeleteMessage, name="delete-message"),

    path('view-projects/', views.ViewProjects, name="projects"),
    path('create-project/', views.CreateProject, name="create-project"),
    path('update-project/<str:pk>/', views.UpdateProject, name="update-project"),
    path('delete-project/<str:pk>/', views.DeleteProject, name="delete-project"),
    
    path('view-stage/<str:pk>/', views.ViewProjectStages, name="project-stages"),
    path('delete-project/stage/<str:pk>/', views.DeleteProjectStage, name="delete-project-stage"),
    path('update-project/stage/<str:pk>/', views.UpdateProjectStage, name="update-project-stage"),

    #anaylsis
    path('analyse/', views.AnalyseView, name="analyse"),

    #access
    path('access/', views.Access, name="access"),
]

