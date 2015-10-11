from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from .helpers import UnicodeWriter, prepareContext
from .models import Project_Shopping_List, Ingredient, Allergen, Meal, Meal_Receipe_Shopping_List

def conv_measurement(measurement, quantity):
	if(measurement == 'n'):
		if(quantity == 1):
			return 'piece'
		return 'pieces'
	return measurement

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
				shopping_item = Meal_Receipe_Shopping_List.objects.get(project_id=context['active_project'].id, meal_id=meal.id, receipe_id=receipe.id, ing_id=ing.id)
			
			
	
	return response

@login_required
def project_shopping_list_csv(request):
	context = prepareContext(request)
	if('active_project' not in context):
		return redirect('cooking:projects')
	
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="shoppinglist.csv"'
	
	writer = UnicodeWriter(response)
	writer.writerow(['Ingredient', 'Exact Amount 1', '', 'Exact Amount 2', '', 'Effective Amount 1', '', 'Effective Amount 2', '', 'Buying Count', 'Effective Price'])
	shoppinglist = Project_Shopping_List.objects.filter(project_id=context['active_project'].id)
	for item in shoppinglist:
		writer.writerow([item.name, 
				  item.exact_amount, 
				  conv_measurement(item.buying_measurement, item.exact_amount),
				  item.exact_calculation_amount(),
				  conv_measurement(item.calculation_measurement, item.exact_calculation_amount()),
				  item.effective_amount,
				  conv_measurement(item.buying_measurement, item.effective_amount),
				  item.effective_calculation_amount(),
				  conv_measurement(item.calculation_measurement, item.effective_calculation_amount()),
				  item.buying_count,
				  item.effective_price])
	
	return response

@login_required
def ingredients_csv(request):
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="ingredients.csv"'
	writer = UnicodeWriter(response)
	writer.writerow(['Name', 'Buying unit', '', 'Calculation unit', '', 'Price', 'Remarks', 'Cheapest Store', 'Allergens'])
	ingredients = Ingredient.objects.all()
	for item in ingredients:
		writer.writerow([item.name,
				   item.buying_quantity,
				   conv_measurement(item.buying_measurement, item.buying_quantity),
				   item.calculation_quantity,
				   conv_measurement(item.calculation_measurement, item.calculation_quantity),
				   item.price,
				   item.remarks,
				   item.cheapest_store,
				   ', '.join([a.name for a in item.allergens.all()])])
	
	return response
	