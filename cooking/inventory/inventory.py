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
from cooking.models import Ingredient, Inventory_Item	
		
class Inventory_ItemForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(Inventory_ItemForm, self).__init__(*args, **kwargs)
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
		model = Inventory_Item
		exclude = ['project']
	
	def clean_measurement(self):
		if(self.cleaned_data.get('ingredient') == None):
			return self.cleaned_data.get('measurement')
		if(self.cleaned_data.get('measurement') == self.cleaned_data.get('ingredient').buying_measurement or self.cleaned_data.get('measurement') == self.cleaned_data.get('ingredient').calculation_measurement):
			return self.cleaned_data.get('measurement')
		else:
			raise forms.ValidationError("Please use only measurements which are set in the ingredient either as calculation or buying measurement")
	
	def clean(self):
		try:
			Inventory_Item.objects.get(project=self.instance.project, ingredient=self.cleaned_data['ingredient'])
		except Inventory_Item.DoesNotExist:
			pass
		else:
			raise forms.ValidationError('This ingredient is already in inventory!')

		return self.cleaned_data
	

def add_to_inventory(proj, item):
	if(item.exact_amount <= 0):
		return
	
	inv = None
	try:
		inv = Inventory_Item.objects.get(project=proj, ingredient=item)
	except Inventory_Item.DoesNotExist:
		inv = Inventory_Item(project=proj, ingredient=item, measurement=item.buying_measurement, amount=0)

	amount = item.exact_amount
	if(item.buying_measurement != inv.measurement):
		amount = (amount / item.calculation_quantity) * item.buying_quantity
		
	inv.amount += amount
	inv.save()
	

def inventory_data(proj):
	return Inventory_Item.objects.filter(Q(project=proj) & Q(ingredient__receipe__meal__project=proj)).annotate(
		exact_amount_tmp=Case(
				When(ingredient__buying_measurement=F('ingredient__receipe_ingredient__measurement'),
					then=(F('ingredient__receipe_ingredient__amount') / F('ingredient__receipe__default_person_count')) * F('ingredient__receipe__meal_receipe__person_count')),
				When(ingredient__calculation_measurement=F('ingredient__receipe_ingredient__measurement'),
					then=(((F('ingredient__receipe_ingredient__amount') / F('ingredient__calculation_quantity')) * F('ingredient__buying_quantity')) / F('ingredient__receipe__default_person_count')) * F('ingredient__receipe__meal_receipe__person_count')),
				default=0,
				output_field=FloatField()),
		).annotate(
			exact_total_amount = Sum(F('exact_amount_tmp'))
		).annotate(
			already_used = Case(
				When(measurement=F('ingredient__buying_measurement'),
					then=F('exact_total_amount')),
				When(measurement=F('ingredient__calculation_measurement'),
					then=(F('exact_total_amount') / F('ingredient__buying_quantity')) * F('ingredient__calculation_quantity')),
				default=0,
				output_field=FloatField()),
			exact_buying_count = Case(
				When(measurement=F('ingredient__buying_measurement'),
					then=F('amount') / F('ingredient__buying_quantity')),
				When(measurement=F('ingredient__calculation_measurement'),
					then=F('amount') / F('ingredient__calculation_quantity')),
				default=0,
				output_field=FloatField()),
			exact_price = Case(
				When(measurement=F('ingredient__buying_measurement'),
					then=(F('amount') / F('ingredient__buying_quantity')) * F('ingredient__price')),
				When(measurement=F('ingredient__calculation_measurement'),
					then=(F('amount') / F('ingredient__calculation_quantity')) * F('ingredient__price')),
				default=0,
				output_field=FloatField()),
		)

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
	context['ingredient_list'] = inventory_data(context['active_project'])
	context['pagetitle'] = 'Inventory'
	context['inventory_active'] = request.session.get('inventory_active', True)
	return render(request, 'listings/inventory.html', context)
