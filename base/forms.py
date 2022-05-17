from distutils.command import clean
from django.forms import ModelForm, TextInput
from .models import Employee, EmployeeAltContact, Department, User, JobRole, SickLeave, Timesheet, Room, Messages, Project, ProjectStage
from django import forms

class UserForm(ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField( label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields=('username',)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match, please try again")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class EmployeeForm(ModelForm):
    class Meta:
        model= Employee
        fields = '__all__'
        exclude  = ['username']

class EmployeeAltContactForm(ModelForm):
    class Meta:
        model= EmployeeAltContact
        fields = '__all__'
        exclude  = ['username']

class DepartmentForm(ModelForm):
    class Meta:
        model= Department
        fields = '__all__'

class JobRoleForm(ModelForm):
    class Meta:
        model= JobRole
        fields = '__all__'

class TimeSheetForm(ModelForm):
    class Meta:
        model= Timesheet
        fields = '__all__'
        exclude  = ['recorded_by']

class DataInput(forms.DateInput):
    input_type = 'date'

class SickLeaveForm(ModelForm):
    class Meta:
        model= SickLeave
        widgets = {'date_from': DataInput(), 'date_to': DataInput}
        fields = '__all__'
        exclude  = ['recorded_by']

class RoomForm(forms.ModelForm):
    class Meta:
        model= Room
        exclude  = ['host']

    room = forms.CharField()
    description = forms.Textarea()
    participants = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )

class MessageForm(ModelForm):
    class Meta:
        model= Messages
        fields = '__all__'

class ProjectForm(forms.ModelForm):
    class Meta:
        model= Project
        exclude  = ['host']

    project = forms.CharField()
    date_from = forms.DateField()
    due_date = forms.DateField()
    participants = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )
    
class ProjectStageForm(ModelForm):
    class Meta:
        model= ProjectStage
        exclude  = ['project']


