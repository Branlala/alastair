from django.core.urlresolvers import resolve, reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, redirect
from .form_statics import IngredientForm, Receipe_IngredientForm, ReceipeForm
from .forms import ConfirmDeleteForm
from .models import Ingredient, Allergen, Receipe, Receipe_Ingredient
from .helpers import prepareContext

@login_required
def list_receipes(request):
	context = prepareContext(request)
	context['receipe_list'] = Receipe.objects.all()
	context['pagetitle'] = 'Receipes'
	return render(request, 'listings/receipes.html', context)

@login_required
def edit_receipe(request, active_receipe):
	context = prepareContext(request)
	if(request.POST and 'id' in request.POST):
		active_receipe = int(request.POST.get('id'))
	rec = Receipe.objects.get(id=active_receipe)
	form = ReceipeForm(request.POST or None, instance=rec)
	if(form.is_valid()):
		form.save()
		context['submitted'] = 1
	context['name'] = rec.name
	context['active_page'] = 'receipes'
	context['form'] = form
	context['pagetitle'] = 'Edit Receipe'
	return render(request, 'single/defaultform.html', context)

@login_required
def del_receipe(request, active_receipe):
	context = prepareContext(request)
	rec = Receipe.objects.get(id=active_receipe)
	form = ConfirmDeleteForm(request.POST or None)
	if(form.is_valid()):
		rec.delete()
		return redirect('cooking:receipes')
	
	context['object'] = rec
	context['noaction'] = reverse('cooking:receipes')
	context['form'] = form
	context['pagetitle'] = 'Delete Receipe'
	return render(request, 'single/confirmdelete.html', context)

@login_required
def new_receipe(request):
	context = prepareContext(request)
	form = None
	if(request.POST):
		form = ReceipeForm(data=request.POST or None)
		if(form.is_valid()):
			form.save()
			return redirect('cooking:receipes')
	else:
		form = ReceipeForm()
	context['name'] ='New Receipe'
	context['active_page'] = 'receipes'
	context['form'] = form
	context['pagetitle'] = 'New Receipe'
	return render(request, 'single/defaultform.html', context)

@login_required
def list_receipe_ingredient(request, active_receipe):
	context = prepareContext(request)
	
	if('remove_receipe_ingredient' in request.GET):
		try:
			Receipe_Ingredient.objects.get(id=int(request.GET.get('remove_receipe_ingredient'))).delete()
		except:
			pass
	
	rec = Receipe.objects.get(id=active_receipe)
	form = Receipe_IngredientForm(request.POST or None)
	if(form.is_valid()):
		obj = form.save(commit=False)
		obj.receipe = rec
		obj.save()
		form = Receipe_IngredientForm(None)
	
	context['form'] = form
	context['receipe'] = rec
	context['receipe_ingredient_list'] = Receipe_Ingredient.objects.filter(receipe=active_receipe)
	context['ingredient_list'] = Ingredient.objects.all()
	context['pagetitle'] = 'Ingredients for Receipe'
	return render(request, 'listings/receipe_ingredient.html', context)


@login_required
def list_ingredients(request):
	context = prepareContext(request)
	context['ingredient_list'] = Ingredient.objects.all()
	context['pagetitle'] = 'Ingredients'
	return render(request, 'listings/ingredients.html', context)

@login_required
def edit_ingredient(request, ingredient):
	context = prepareContext(request)
	if(request.POST and 'id' in request.POST):
		ingredient = int(request.POST.get('id'))
	ing = Ingredient.objects.get(id=ingredient)
	form = IngredientForm(request.POST or None, instance=ing)
	if(form.is_valid()):
		form.save()
		context['submitted'] = True
	context['form'] = form
	context['name'] = ing.name
	context['pagetitle'] = 'Edit Ingredient'
	return render(request, 'single/defaultform.html', context)

@login_required
def del_ingredient(request, ingredient):
	context = prepareContext(request)
	ing = Ingredient.objects.get(id=ingredient)
	form = ConfirmDeleteForm(request.POST or None)
	if(form.is_valid()):
		ing.delete()
		return redirect('cooking:ingredients')
	
	context['object'] = ing
	context['noaction'] = reverse('cooking:ingredients')
	context['form'] = form
	context['pagetitle'] = 'Delete Ingredient'
	return render(request, 'single/confirmdelete.html', context)

@login_required
def new_ingredient(request):
	context = prepareContext(request)
	form = None
	if(request.POST):
		form = IngredientForm(data=request.POST or None)
		if(form.is_valid()):
			form.save()
			return redirect('cooking:ingredients')
	else:
		form = IngredientForm()
	
	context['form'] = form
	context['name'] = 'New Ingredient'
	context['pagetitle'] = 'New Ingredient'
	return render(request, 'single/defaultform.html', context)
	
@login_required
def list_allergens(request):
	context = prepareContext(request)
	context['allergen_list'] = Allergen.objects.all()
	context['pagetitle'] = 'Allergens'
	return render(request, 'listings/allergens.html', context)

