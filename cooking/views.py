#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.urlresolvers import resolve, reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.template.defaulttags import register
from .models import Project, Meal, Project_Readonly, Project_Shopping_List, Project_Shopping_List_Invsub, Meal_Receipe, Meal_Receipe_Shopping_List, Receipe, Inventory_Item
from .forms import ProjectForm, MealForm, ConfirmDeleteForm, Meal_ReceipeForm, Inventory_ItemForm
from .helpers import prepareContext


def hello(request):
	return render(request, 'base_listing.html', {'title':'Hallo Welt'})

@login_required
def list_projects(request):
	context = prepareContext(request)
	context['project_list'] = Project.objects.all()
	context['pagetitle'] = 'Overview'
	return render(request, 'listings/projects.html', context)

@login_required
def edit_project(request, project):
	context = prepareContext(request)
	if(request.POST and 'id' in request.POST):
		project = int(request.POST.get('id'))
	proj = Project.objects.get(id=project)
	form = ProjectForm(request.POST or None, instance=proj)
	if(form.is_valid()):
		form.save()
		context['submitted'] = True
	context['form'] = form
	context['name'] = proj.name
	context['pagetitle'] = 'Edit Project'
	return render(request, 'single/defaultform.html', context)

@login_required
def del_project(request, project):
	context = prepareContext(request)
	proj = Project.objects.get(id=project)
	form = ConfirmDeleteForm(request.POST or None)
	if(form.is_valid()):
		proj.delete()
		try:
			del request.session['active_project']
		except:
			pass
		return redirect('cooking:projects')
	
	
	context['object'] = proj
	context['noaction'] = reverse('cooking:projects')
	context['form'] = form
	context['pagetitle'] = 'Delete Project'
	return render(request, 'single/confirmdelete.html', context)

@login_required
def new_project(request):
	context = prepareContext(request)
	form = None
	if(request.POST):
		form = ProjectForm(data=request.POST or None)
		if(form.is_valid()):
			form.save()
			return redirect('cooking:projects')
	else:
		form = ProjectForm()
	
	context['form'] = form
	context['name'] = 'New Project'
	context['pagetitle'] = 'New Project'
	return render(request, 'single/defaultform.html', context)

@login_required
def list_meals(request):
	context = prepareContext(request)
	if('active_project' not in context):
		return redirect('cooking:projects')
	context['meals_list'] = Meal.objects.filter(project=context['active_project'])
	context['pagetitle'] = 'Meals'
	return render(request, 'listings/meals.html', context)

@login_required
def edit_meal(request, meal):
	context = prepareContext(request)
	if(request.POST and 'id' in request.POST):
		meal = int(request.POST.get('id'))
	m = Meal.objects.get(id=meal)
	form = MealForm(request.POST or None, instance=m)
	if(form.is_valid()):
		form.save()
		context['submitted'] = True
	context['form'] = form
	context['meal'] = m
	context['name'] = m.name
	context['pagetitle'] = 'Edit Meal'
	return render(request, 'single/defaultform.html', context)

@login_required
def del_meal(request, meal):
	context = prepareContext(request)
	m = Meal.objects.get(id=meal)
	form = ConfirmDeleteForm(request.POST or None)
	if(form.is_valid()):
		m.delete()
		return redirect('cooking:meals')
	
	context['object'] = m
	context['noaction'] = reverse('cooking:meals')
	context['form'] = form
	context['pagetitle'] = 'Delete Meal'
	return render(request, 'single/confirmdelete.html', context)

@login_required
def new_meal(request):
	context = prepareContext(request)
	form = None
	meal = Meal(project=context['active_project'])
	if(request.POST):
		form = MealForm(data=request.POST or None, instance=meal)
		if(form.is_valid()):
			form.save()
			return redirect('cooking:meals')
	else:
		form = MealForm(instance=meal)
	
	context['form'] = form
	context['name'] = 'New Meal'
	context['pagetitle'] = 'New Meal'
	return render(request, 'single/defaultform.html', context)

@login_required
def list_meal_receipe(request, meal):
	context = prepareContext(request)
	
	if('remove_meal_receipe' in request.GET):
		try:
			Meal_Receipe.objects.get(id=int(request.GET.get('remove_meal_receipe'))).delete()
		except:
			pass
	
	m = Meal.objects.get(id=meal)
	m_rec = Meal_Receipe(meal=m)
	form = Meal_ReceipeForm(request.POST or None, instance=m_rec)
	if(form.is_valid()):
		form.save()
		form = Meal_ReceipeForm(None)
	
	context['form'] = form
	context['meal'] = m
	context['meal_receipe_list'] = Meal_Receipe.objects.filter(meal=m)
	context['pagetitle'] = 'Receipes in Meal'
	return render(request, 'listings/meal_receipe.html', context)

@login_required
def meal_receipe_shopping_list(request, meal, receipe):
	context = prepareContext(request)
	if('active_project' not in context):
		return redirect('cooking:projects')
	context['shopping_list'] = Meal_Receipe_Shopping_List.objects.filter(project_id=context['active_project'].id, meal_id=meal, receipe_id=receipe)
	context['total_exact_price'] = context['shopping_list'].aggregate(tp=Sum('exact_price')).get('tp')
	context['total_effective_price'] = context['shopping_list'].aggregate(tp=Sum('effective_price')).get('tp')
	context['meal'] = Meal.objects.get(id=meal)
	context['receipe'] = Receipe.objects.get(id=receipe)
	context['pagetitle'] = 'Meal-specific Shopping List'
	return render(request, 'listings/meal_receipe_shopping_list.html', context)

@login_required
def project_shopping_list(request):
	context = prepareContext(request)
	if('active_project' not in context):
		return redirect('cooking:projects')
	if('inventory_active' not in request.session):
		request.session['inventory_active'] = True
	if(request.session['inventory_active']):
		context['shopping_list'] = Project_Shopping_List_Invsub.objects.filter(project_id=context['active_project'].id).exclude(exact_amount=0)
	else:
		context['shopping_list'] = Project_Shopping_List.objects.filter(project_id=context['active_project'].id)
	context['total_exact_price'] = context['shopping_list'].aggregate(tp=Sum('exact_price')).get('tp')
	context['total_effective_price'] = context['shopping_list'].aggregate(tp=Sum('effective_price')).get('tp')
	context['pagetitle'] = 'Shopping List'
	context['inventory_active'] = request.session['inventory_active']
	return render(request, 'listings/shopping_list.html', context)

@login_required
def inventory(request):
	context = prepareContext(request)
	if('inventory_active' not in request.session):
		request.session['inventory_active'] = True
	if('remove_inventory_ingredient' in request.GET):
		try:
			Inventory_Item.objects.get(id=int(request.GET.get('remove_inventory_ingredient'))).delete()
		except:
			pass
	
	if('activate_inventory' in request.GET):
		request.session['inventory_active'] = True
	elif('deactivate_inventory' in request.GET):
		request.session['inventory_active'] = False
	
	if('active_project' not in context):
		return redirect('cooking:projects')
	
	inv = Inventory_Item(project=context['active_project'])
	form = Inventory_ItemForm(request.POST or None, instance=inv)
	if(form.is_valid()):
		form.save()
		inv = Inventory_Item(project=context['active_project'])
		form = Inventory_ItemForm(None, instance=inv)
	
	context['form'] = form
	context['ingredient_list'] = Inventory_Item.objects.all()
	context['pagetitle'] = 'Inventory'
	context['inventory_active'] = request.session.get('inventory_active', True)
	return render(request, 'listings/inventory.html', context)
