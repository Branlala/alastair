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
class Allergen(models.Model):
	name = models.CharField(max_length=256)
	def __str__(self):
		return self.name
	
	class Meta:
		ordering = ['name']
		
	
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
