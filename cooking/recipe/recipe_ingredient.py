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
from cooking.models import Receipe_Ingredient, Allergen
from .recipe import receipe_data


class Receipe_IngredientForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(Receipe_IngredientForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_class = 'form-inline'
		self.helper.field_template = 'bootstrap3/layout/inline_field.html'
		self.helper.form_method = 'post'
		self.helper.form_action = ''
		self.helper.layout = Layout(
			HTML('<td>'),
			InlineField('ingredient', title='Name'), 
			HTML('</td><td>'),
			Div(
				Div(InlineField('amount'), css_class='col-md-6'), 
				Div(InlineField('measurement'), css_class='col-md-6'),
				css_class='row'
			),
			HTML('</td><td></td><td></td><td>'),
			InlineField('remarks'),
			HTML('</td><td>'),
			StrictButton('<span class="glyphicon glyphicon-plus" aria-hidden="true"></span><span class="sr-only">Add</span>', type='submit', css_class='btn btn-default btn-sm'),
			HTML('</td>')
			)
	
	class Meta:
		model = Receipe_Ingredient
		exclude = ['receipe']
	
	def clean_measurement(self):
		if(self.cleaned_data.get('ingredient') == None):
			return self.cleaned_data.get('measurement')
		if(self.cleaned_data.get('measurement') == self.cleaned_data.get('ingredient').buying_measurement or self.cleaned_data.get('measurement') == self.cleaned_data.get('ingredient').calculation_measurement):
			return self.cleaned_data.get('measurement')
		else:
			raise forms.ValidationError("Please use only measurements which are set in the ingredient either as calculation or buying measurement")
		


@login_required
def list_receipe_ingredient(request, active_receipe):
	context = prepareContext(request)
	
	if('remove_receipe_ingredient' in request.GET):
		try:
			Receipe_Ingredient.objects.get(id=int(request.GET.get('remove_receipe_ingredient'))).delete()
		except:
			pass
	
	rec = receipe_data().get(id=active_receipe)
	form = Receipe_IngredientForm(request.POST or None)
	if(form.is_valid()):
		obj = form.save(commit=False)
		obj.receipe = rec
		obj.save()
		form = Receipe_IngredientForm(None)
	
	context['form'] = form
	context['receipe'] = rec
	context['receipe_ingredient_list'] = Receipe_Ingredient.objects.filter(receipe=rec).annotate(
			usage_count=Case(
				When(measurement=F('ingredient__calculation_measurement'), then=F('amount')/F('ingredient__calculation_quantity')),
				When(measurement=F('ingredient__buying_measurement'), then=F('amount')/F('ingredient__buying_quantity')),
				default=0,
				output_field=FloatField()
				)
		).annotate(
			price_per_person=ExpressionWrapper((F('usage_count') * F('ingredient__price'))/F('receipe__default_person_count'), output_field=FloatField()),
			weight_per_person=ExpressionWrapper((F('usage_count') * F('ingredient__cooked_weight'))/F('receipe__default_person_count'), output_field=FloatField()),
		)
	context['allergen_list'] = Allergen.objects.filter(ingredient__receipe=rec).distinct()
	for allergen in context['allergen_list']:
		allergen.used_in = ', '.join([x.name for x in allergen.ingredient_set.filter(receipe=rec)])
	context['pagetitle'] = 'Ingredients for Receipe'
	return render(request, 'listings/receipe_ingredient.html', context)
