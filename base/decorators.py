from django.http import HttpResponse 
from django.shortcuts import render, redirect

# checks if the user is an admin - then will render the view
# otherwise will render the no access page
def admin_only(view_func):
	def wrapper_function(request, *args, **kwargs):
		group = None
		if request.user.groups.exists():
			group = request.user.groups.all()[0].name
    
		if group != 'admin':
			return redirect('access')

		if group == 'admin':
			return view_func(request, *args, **kwargs)

	return wrapper_function
 