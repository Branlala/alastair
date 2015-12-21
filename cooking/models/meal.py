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
class Meal(models.Model):
	name = models.CharField(max_length=256)
	time = models.DateTimeField(blank=True, null=True)
	project = models.ForeignKey(Project)
	used_receipes = models.ManyToManyField(Receipe, through='Meal_Receipe', blank=True)
	
	def __str__(self):
		return self.name
	
	class Meta:
		ordering = ['time', 'name']
		
		
			
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
	
	
@login_required
def list_meals(request):
	context = prepareContext(request)
	if('active_project' not in context):
		return redirect('cooking:projects')
	context['meals_list'] = Meal.objects.filter(project=context['active_project'])
	context['pagetitle'] = 'Meals'
	return render(request, 'listings/meals.html', context)

@login_required
def edit_meal(request, meal):
	context = prepareContext(request)
	if(request.POST and 'id' in request.POST):
		meal = int(request.POST.get('id'))
	m = Meal.objects.get(id=meal)
	form = MealForm(request.POST or None, instance=m)
	if(form.is_valid()):
		form.save()
		context['submitted'] = True
	context['form'] = form
	context['meal'] = m
	context['name'] = m.name
	context['pagetitle'] = 'Edit Meal'
	return render(request, 'single/defaultform.html', context)

@login_required
def del_meal(request, meal):
	context = prepareContext(request)
	m = Meal.objects.get(id=meal)
	form = ConfirmDeleteForm(request.POST or None)
	if(form.is_valid()):
		m.delete()
		return redirect('cooking:meals')
	
	context['object'] = m
	context['noaction'] = reverse('cooking:meals')
	context['form'] = form
	context['pagetitle'] = 'Delete Meal'
	return render(request, 'single/confirmdelete.html', context)

@login_required
def new_meal(request):
	context = prepareContext(request)
	form = None
	meal = Meal(project=context['active_project'])
	if(request.POST):
		form = MealForm(data=request.POST or None, instance=meal)
		if(form.is_valid()):
			form.save()
			return redirect('cooking:meals')
	else:
		form = MealForm(instance=meal)
	
	context['form'] = form
	context['name'] = 'New Meal'
	context['pagetitle'] = 'New Meal'
	return render(request, 'single/defaultform.html', context)
