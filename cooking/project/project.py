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

@python_2_unicode_compatible
class Project(models.Model):
	name = models.CharField(max_length=256)
	start_date = models.DateField(blank=True, null=True)
	end_date = models.DateField(blank=True, null=True)
	def __str__(self):
		return self.name
	
	class Meta:
		ordering = ['start_date', 'name']
		
		
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
		
@login_required
def list_projects(request):
	context = prepareContext(request)
	context['project_list'] = Project.objects.all()
	context['pagetitle'] = 'Overview'
	return render(request, 'listings/projects.html', context)

@login_required
def edit_project(request, project):
	context = prepareContext(request)
	if(request.POST and 'id' in request.POST):
		project = int(request.POST.get('id'))
	proj = Project.objects.get(id=project)
	form = ProjectForm(request.POST or None, instance=proj)
	if(form.is_valid()):
		form.save()
		context['submitted'] = True
	context['form'] = form
	context['name'] = proj.name
	context['pagetitle'] = 'Edit Project'
	return render(request, 'single/defaultform.html', context)

@login_required
def del_project(request, project):
	context = prepareContext(request)
	proj = Project.objects.get(id=project)
	form = ConfirmDeleteForm(request.POST or None)
	if(form.is_valid()):
		proj.delete()
		try:
			del request.session['active_project']
		except:
			pass
		return redirect('cooking:projects')
	
	
	context['object'] = proj
	context['noaction'] = reverse('cooking:projects')
	context['form'] = form
	context['pagetitle'] = 'Delete Project'
	return render(request, 'single/confirmdelete.html', context)

@login_required
def new_project(request):
	context = prepareContext(request)
	form = None
	if(request.POST):
		form = ProjectForm(data=request.POST or None)
		if(form.is_valid()):
			form.save()
			return redirect('cooking:projects')
	else:
		form = ProjectForm()
	
	context['form'] = form
	context['name'] = 'New Project'
	context['pagetitle'] = 'New Project'
	return render(request, 'single/defaultform.html', context)

@login_required
def project_csv(request):
	context = prepareContext(request)
	if('active_project' not in context):
		return redirect('cooking:projects')
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="' + context['active_project'].name + '.csv"'
	
	writer = UnicodeWriter(response)
	
	allmeals = Meal.objects.filter(project=context['active_project'])
	for meal in allmeals:
		allreceipes = meal.used_receipes.all()
		for receipe in allreceipes:
			allingredients = receipe.ingredients.all()
			for ing in allingredients:
				#shopping_item = Meal_Receipe_Shopping_List.objects.get(project_id=context['active_project'].id, meal_id=meal.id, receipe_id=receipe.id, ing_id=ing.id)
				pass
			
	
	return response