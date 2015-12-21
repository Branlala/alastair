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
from cooking.models import Meal_Receipe, Ingredient, Meal

		
class Meal_ReceipeForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(Meal_ReceipeForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_class = 'form-inline'
		self.helper.field_template = 'bootstrap3/layout/inline_field.html'
		self.helper.form_method = 'post'
		self.helper.form_action = ''
		self.helper.layout = Layout(
			HTML('<td>'),
			InlineField('receipe'), 
			HTML('</td><td>'),
			InlineField('person_count'),
			HTML('</td><td></td><td></td><td>'),
			InlineField('remarks'),
			HTML('</td><td>'),
			StrictButton('<span class="glyphicon glyphicon-plus" aria-hidden="true"></span><span class="sr-only">Add</span>', type='submit', css_class='btn btn-default btn-sm'),
			HTML('</td>')
			)
	
	class Meta:
		model = Meal_Receipe
		exclude = ['meal']
	
def meal_receipe_data(m):
	return Meal_Receipe.objects.filter(meal=m).annotate(
		my_usage_count=Case(
				When(receipe__receipe_ingredient__measurement=F('receipe__ingredients__calculation_measurement'), then=F('receipe__receipe_ingredient__amount')/F('receipe__ingredients__calculation_quantity')),
				When(receipe__receipe_ingredient__measurement=F('receipe__ingredients__buying_measurement'), then=F('receipe__receipe_ingredient__amount')/F('receipe__ingredients__buying_quantity')),
				default=0,
				output_field=FloatField()
				),
		).annotate(
			my_price = ExpressionWrapper(F('my_usage_count') * F('receipe__ingredients__price'), output_field=FloatField()),
			my_weight = ExpressionWrapper(F('my_usage_count') * F('receipe__ingredients__cooked_weight'), output_field=FloatField()),
		).annotate(
			total_weight=Sum(F('my_weight'), output_field=FloatField()),
			total_price=Sum(F('my_price'), output_field=FloatField()),
		).annotate(
			price_per_person=ExpressionWrapper(F('total_price')/F('receipe__default_person_count'), output_field=FloatField()),
			weight_per_person=ExpressionWrapper(F('total_weight')/F('receipe__default_person_count'), output_field=FloatField()),
		)
		

def meal_shopping_list(meal, receipe):
	return Ingredient.objects.filter(receipe=receipe, receipe__meal=meal).annotate(
			usage_count=Case(
				When(buying_measurement=F('receipe_ingredient__measurement'),
					then=((F('receipe_ingredient__amount') / F('buying_quantity')) / F('receipe__default_person_count')) * F('receipe__meal_receipe__person_count')),
				When(calculation_measurement=F('receipe_ingredient__measurement'),
					then=((F('receipe_ingredient__amount') / F('calculation_quantity')) / F('receipe__default_person_count')) * F('receipe__meal_receipe__person_count')),
				default=0,
				output_field=FloatField()),
		).annotate(
		# Copy ri.measurement for easier access
		measurement=F('receipe_ingredient__measurement'),
		# Also copy ri.remarks for easier access
		mr_remarks=F('receipe_ingredient__remarks'),
		exact_amount=F('usage_count') * F('buying_quantity'),
		exact_calculation_amount=Case(
			When(calculation_measurement__isnull=True,
				 then=None),
			default=F('usage_count') * F('calculation_quantity'),
			output_field=FloatField()),
		exact_price=ExpressionWrapper(F('usage_count') * F('price'), output_field=FloatField()),	

		)


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
	context['meal_receipe_list'] = meal_receipe_data(m)
	context['pagetitle'] = 'Receipes in Meal'
	return render(request, 'listings/meal_receipe.html', context)

@login_required
def meal_receipe_shopping_list(request, meal, receipe):
	context = prepareContext(request)
	if('active_project' not in context):
		return redirect('cooking:projects')
	
	#context['shopping_list'] = Meal_Receipe_Shopping_List.objects.filter(project_id=context['active_project'].id, meal_id=meal, receipe_id=receipe)
	context['meal'] = Meal.objects.get(id=meal)
	context['receipe'] = Receipe.objects.get(id=receipe)
	context['shopping_list'] = meal_shopping_list(context['meal'], context['receipe'])
	context['total_exact_price'] = context['shopping_list'].aggregate(tp=Sum('exact_price')).get('tp')
	context['allergen_list'] = Allergen.objects.filter(ingredient__receipe=context['receipe']).distinct()
	for allergen in context['allergen_list']:
		allergen.used_in = ', '.join([x.name for x in allergen.ingredient_set.filter(receipe=context['receipe'])])
	context['pagetitle'] = 'Meal-specific Shopping List'
	return render(request, 'listings/meal_receipe_shopping_list.html', context)
