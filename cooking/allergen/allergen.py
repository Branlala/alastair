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
from cooking.models import Allergen

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
		
	
@login_required
def list_allergens(request):
	context = prepareContext(request)
	
	if('remove_allergen' in request.GET):
		try:
			Allergen.objects.get(id=int(request.GET.get('remove_allergen'))).delete()
		except:
			pass
	
	form = AllergenForm(request.POST or None)
	if(form.is_valid()):
		form.save()
		form = AllergenForm(None)
	
	context['form'] = form
	context['allergen_list'] = Allergen.objects.all()
	context['pagetitle'] = 'Allergens'
	return render(request, 'listings/allergens.html', context)
