from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect

def home(request):
	context = {}
	context['pagetitle'] = 'Home'
	return render(request, 'single/home.html', context)

def tutorial(request):
	context = {}
	context['pagetitle'] = 'Help'
	return render(request, 'single/help.html', context)

def impressum(request):
	context = {}
	context['pagetitle'] = 'Impressum'
	return render(request, 'single/impressum.html', context)

def logout_view(request):
	logout(request)
	return redirect('home')