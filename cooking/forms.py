from django import forms
from django.core.urlresolvers import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Button, Field, Hidden, HTML, Div
from crispy_forms.bootstrap import FormActions, AppendedText, StrictButton,  InlineField
from cooking.models import Project, Meal, Meal_Receipe, Inventory_Item

class ConfirmDeleteForm(forms.Form):

	def __init__(self, *args, **kwargs):
		super(ConfirmDeleteForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_class = 'form-inline'
		self.helper.field_template = 'bootstrap3/layout/inline_field.html'
		self.helper.form_method = 'post'
		self.helper.form_action = ''
		self.helper.layout = Layout(
			HTML('<input type="hidden" name="object_id" value="{% firstof object.id objectid %}" />'),
			FormActions(
				Submit('save', 'Yes', css_class='btn btn_success'),
				HTML('<a href="{{ noaction }}" class="btn btn-default">No</a>')
				),
			)
			
class ProjectForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(ProjectForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_class = 'form-horizontal'
		self.helper.form_method = 'post'
		self.helper.form_action = ''
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-4'
		self.helper.layout = Layout(
				'name',
				Field('start_date', placeholder='yyyy-mm-dd'),
				Field('end_date', placeholder='yyyy-mm-dd'),
				FormActions(
					Submit('save', 'Save Changes'),
					HTML('<a href="' + reverse('cooking:projects') + '" class="btn btn-default" role="button">Cancel</a>'),
					)
		)	
	class Meta:
		model = Project
		exclude = []
			
class MealForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(MealForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_class = 'form-horizontal'
		self.helper.form_method = 'post'
		self.helper.form_action = ''
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-4'
		self.helper.layout = Layout(
				'name',
				Field('time', placeholder='yyyy-mm-dd hh:mm'),
				Field('project', required=True),
				FormActions(
					Submit('save', 'Save Changes'),
					HTML('<a href="' + reverse('cooking:meals') + '" class="btn btn-default" role="button">Cancel</a>'),
					HTML('{% if meal.id %}<a href="{% url "cooking:meals" meal.id %}" class="btn btn-default" role="button">Choose Receipe</a>{% endif %}')
					)
		)	
	class Meta:
		model = Meal
		exclude = ['used_receipes', 'project']
		
		
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
			HTML('</td><td>'),
			InlineField('remarks'),
			HTML('</td><td>'),
			StrictButton('<span class="glyphicon glyphicon-plus" aria-hidden="true"></span><span class="sr-only">Add</span>', type='submit', css_class='btn btn-default btn-sm'),
			HTML('</td>')
			)
	
	class Meta:
		model = Meal_Receipe
		exclude = ['meal']
		
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
			HTML('</td><td></td><td>'),
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