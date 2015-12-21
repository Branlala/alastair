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
from cooking.helpers import prepareContext
from cooking.models import Ingredient
from cooking.forms import ConfirmDeleteForm

class IngredientForm(forms.ModelForm):
	
	def __init__(self, *args, **kwargs):
		super(IngredientForm, self).__init__(*args, **kwargs)
		self.fields['cooked_weight'].required = False
		self.helper = FormHelper()
		self.helper.form_class = 'form-horizontal'
		self.helper.form_method = 'post'
		self.helper.form_action = ''
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-4'
		self.helper.layout = Layout(
			Field('name'),
			Field('buying_quantity'),
			Field('buying_measurement'),
			Field('calculation_quantity'),
			Field('calculation_measurement'),
			AppendedText('cooked_weight', 'Gram'),
			AppendedText('price', '€'),
			Field('cheapest_store'),
			Field('remarks'),
			Field('allergens'),
			FormActions(
				Submit('save', 'Save changes'),
				HTML('<a href="' + reverse('cooking:ingredients') + '" class="btn btn-default" role="button">Cancel</a>'),
			)
		)
		#self.helper.add_input(Submit('submit', 'Save'))
	
	def clean_price(self):
		if(self.cleaned_data.get('price') < 0):
			raise forms.ValidationError("Price can't be negative")
		return self.cleaned_data.get('price')
	
	def clean_buying_quantity(self):
		if(self.cleaned_data.get('buying_quantity') == 0):
			raise forms.ValidationError("Buying Quantity can't be zero")
		return self.cleaned_data.get('buying_quantity')
	
	def clean_calculation_quantity(self):
		if(self.cleaned_data.get('calculation_quantity') != None and self.cleaned_data.get('calculation_quantity') == 0):
			raise forms.ValidationError("Calculation Quantity can not be zero, leave it out if you don't need it")
		return self.cleaned_data.get('calculation_quantity')
	
	def clean_calculation_measurement(self):
		if(self.cleaned_data.get('calculation_measurement') == None and self.cleaned_data.get('calculation_quantity') != None):
			raise forms.ValidationError('If calculation quantity is set, you also need to set the measurement')
		elif(self.cleaned_data.get('calculation_quantity') == None and self.cleaned_data.get('calculation_measurement') != None):
			raise forms.ValidationError('You can not set a measurement without a quantity')
		else:
			return self.cleaned_data.get('calculation_measurement')

	def clean_cooked_weight(self):
		if(self.cleaned_data.get('cooked_weight') == None):
			self.cleaned_data['cooked_weight'] = 0
		return self.cleaned_data.get('cooked_weight')
	
	class Meta:
		model = Ingredient
		exclude = ['id']
		

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
	