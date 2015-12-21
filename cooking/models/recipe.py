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
class Receipe(models.Model):
	name = models.CharField(max_length=256)
	default_person_count = models.IntegerField(default=1, validators=[validate_greater_zero])
	instructions = models.TextField()
	ingredients = models.ManyToManyField(Ingredient, through='Receipe_Ingredient')
	rewrite_weight_per_person = models.FloatField(blank=True, null=True)
	
	def __str__(self):
		return self.name
	
	class Meta:
		ordering = ['name']
	

def receipe_data() :
	return Receipe.objects.all().annotate(
		my_usage_count=Case(
				When(receipe_ingredient__measurement=F('ingredients__calculation_measurement'), then=F('receipe_ingredient__amount')/F('ingredients__calculation_quantity')),
				When(receipe_ingredient__measurement=F('ingredients__buying_measurement'), then=F('receipe_ingredient__amount')/F('ingredients__buying_quantity')),
				default=0,
				output_field=FloatField()
				),
		).annotate(
			my_price = ExpressionWrapper(F('my_usage_count') * F('ingredients__price'), output_field=FloatField()),
			my_weight = ExpressionWrapper(F('my_usage_count') * F('ingredients__cooked_weight'), output_field=FloatField()),
		).annotate(
			total_weight=Sum(F('my_weight'), output_field=FloatField()),
			total_price=Sum(F('my_price'), output_field=FloatField()),
		).annotate(
			price_per_person=ExpressionWrapper(F('total_price')/F('default_person_count'), output_field=FloatField()),
			weight_per_person=ExpressionWrapper(F('total_weight')/F('default_person_count'), output_field=FloatField()),
		)
		
	
@login_required
def list_receipes(request):
	context = prepareContext(request)
	context['receipe_list'] = receipe_data()
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
