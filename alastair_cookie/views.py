from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

def home(request):
	context = {}
	context['pagetitle'] = 'Home'
	return render(request, 'single/home.html', context)

def impressum(request):
	context = {}
	context['pagetitle'] = 'Impressum'
	return render(request, 'single/impressum.html', context)