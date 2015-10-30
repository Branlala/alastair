#encoding=utf8

from django import forms
from django.core.urlresolvers import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Button, Field, Hidden, HTML, Div
from crispy_forms.bootstrap import FormActions, AppendedText, StrictButton,  InlineField
from cooking.models import Receipe_Ingredient, Ingredient, Receipe, Allergen

class ReceipeForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(ReceipeForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_class = 'form-horizontal'
		self.helper.form_method = 'post'
		self.helper.form_action = ''
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-4'
		self.helper.layout = Layout(
			'name',
			'default_person_count',
			'instructions',
			FormActions(
				Submit('save', 'Save changes'),
				HTML('<a href="' + reverse('cooking:receipes') + '" class="btn btn-default" role="button">Cancel</a>'),
			),
		)
			
	def clean_default_person_count(self):
		if(int(self.cleaned_data.get('default_person_count')) > 0):
			return self.cleaned_data.get('default_person_count')
		else:
			raise forms.ValidationError('Person count must be greater or equals 1')
		
	class Meta:
		model = Receipe
		exclude = ['id', 'ingredients']

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
			HTML('</td><td>'),
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
		
class IngredientForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(IngredientForm, self).__init__(*args, **kwargs)
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

	class Meta:
		model = Ingredient
		exclude = ['id']
		
		
class AllergenForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(AllergenForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_class = 'form-inline'
		self.helper.field_template = 'bootstrap3/layout/inline_field.html'
		self.helper.form_method = 'post'
		self.helper.form_action = ''
		self.helper.layout = Layout(
			HTML('<td>'),
			InlineField('name'), 
			HTML('</td><td>'),
			StrictButton('<span class="glyphicon glyphicon-plus" aria-hidden="true"></span><span class="sr-only">Add</span>', type='submit', css_class='btn btn-default btn-sm'),
			HTML('</td>'),
		)
		
	class Meta:
		model = Allergen
		exclude = []
		
		