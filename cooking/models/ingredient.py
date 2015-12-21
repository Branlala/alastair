from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Button, Field, Hidden, HTML, Div
from crispy_forms.bootstrap import FormActions, AppendedText, StrictButton,  InlineField
from django import forms
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import resolve, reverse
from django.db import models
from django.db.models import F, ExpressionWrapper, FloatField, IntegerField, CharField, Case, When, Sum, Func, Min, Q
from django.shortcuts import render, redirect
from django.utils.encoding import python_2_unicode_compatible
from .helpers import prepareContext


@python_2_unicode_compatible
class Ingredient(models.Model):
	name = models.CharField(max_length=256)
	buying_quantity = models.FloatField(validators=[validate_greater_zero])
	buying_measurement = models.CharField(max_length=2, choices=MEASUREMENTS)
	calculation_quantity = models.FloatField(blank=True, null=True, validators=[validate_greater_zero])
	calculation_measurement = models.CharField(max_length=2, choices=MEASUREMENTS, blank=True, null=True)	
	price = models.DecimalField(max_digits=8, decimal_places=2, validators=[validate_positive])
	cheapest_store = models.CharField(max_length=256, blank=True)
	remarks = models.CharField(max_length=256, blank=True)
	allergens = models.ManyToManyField(Allergen, blank=True)
	cooked_weight = models.FloatField(default=0, validators=[validate_positive])

	def __str__(self):
		return self.name
	
	class Meta:
		ordering = ['name']
	

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
def ingredients_csv(request):
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="ingredients.csv"'
	writer = UnicodeWriter(response)
	writer.writerow(['Name', 'Buying unit', '', 'Calculation unit', '', 'Price', 'Remarks', 'Cheapest Store', 'Allergens'])
	ingredients = Ingredient.objects.all()
	for item in ingredients:
		writer.writerow([item.name,
				   item.buying_quantity,
				   conv_measurement(item.buying_measurement, item.buying_quantity),
				   item.calculation_quantity,
				   conv_measurement(item.calculation_measurement, item.calculation_quantity),
				   item.price,
				   item.remarks,
				   item.cheapest_store,
				   ', '.join([a.name for a in item.allergens.all()])])
	
	return response
	