import math
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
from cooking.helpers import conv_measurement
from cooking.models import Ingredient
from cooking.inventory.inventory import inventory_data, add_to_inventory
from io import StringIO
import csv, codecs
from django.http import HttpResponse

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        #for row in rows:
        #self.writer.writerow(row)
        #self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        #data = data.decode("utf-8", "strict")
        # ... and reencode it into the target encoding
        #data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

def project_shopping_list_data(proj):
		return Ingredient.objects.filter(receipe__meal__project=proj).annotate(
			# Copy ri.measurement for easier access
			measurement=F('receipe_ingredient__measurement'),
			# Also copy ri.remarks for easier access
			mr_remarks=F('receipe_ingredient__remarks'),
			# Exact price = (mr.person_count / r.default_person_count) * i.price
			exact_price_tmp=ExpressionWrapper((F('receipe__meal_receipe__person_count') / F('receipe__default_person_count')) * F('price'), output_field=FloatField()),

			exact_amount_tmp=Case(
				When(buying_measurement=F('receipe_ingredient__measurement'),
					then=(F('receipe_ingredient__amount') / F('receipe__default_person_count')) * F('receipe__meal_receipe__person_count')),
				When(calculation_measurement=F('receipe_ingredient__measurement'),
					then=(((F('receipe_ingredient__amount') / F('calculation_quantity')) * F('buying_quantity')) / F('receipe__default_person_count')) * F('receipe__meal_receipe__person_count')),
				default=0,
				output_field=FloatField()),
			exact_calculation_amount_tmp=Case(
				When(calculation_measurement__isnull=True,
					then=None),
				When(buying_measurement=F('receipe_ingredient__measurement'),
					then=(((F('receipe_ingredient__amount') / F('buying_quantity')) * F('calculation_quantity')) / F('receipe__default_person_count')) * F('receipe__meal_receipe__person_count')),
				When(calculation_measurement=F('receipe_ingredient__measurement'),
					then=(F('receipe_ingredient__amount') / F('receipe__default_person_count')) * F('receipe__meal_receipe__person_count')),
				default=None,
				output_field=FloatField()),
		).annotate(
			exact_amount=Sum('exact_amount_tmp'),
			first_occurrence=Min('receipe__meal__time'),
		).annotate(
			exact_calculation_amount=Case(When(calculation_measurement__isnull=False, then=F('exact_amount') / F('buying_quantity') * F('calculation_quantity')),
										default=None,
										output_field=FloatField()),
			exact_buying_count=(F('exact_amount') / F('buying_quantity')),
			buying_count=Func((F('exact_amount') / F('buying_quantity')) + 0.5, function='ROUND'),
		).annotate(
			effective_amount=F('buying_count') * F('buying_quantity'),
			effective_calculation_amount=F('buying_count') * F('calculation_quantity'),
			effective_price=ExpressionWrapper(F('buying_count') * F('price'), output_field=FloatField()),
		#).values('first_occurrence', 'name', 'id', 'buying_measurement', 'buying_quantity', 'calculation_measurement', 'calculation_quantity', 'exact_amount', 'exact_calculation_amount', 'effective_amount', 'effective_calculation_amount', 'remarks', 'effective_price', 'buying_count', 'price'
		)


def subtract_inventory(proj, shopping_list):
	inventory = list(inventory_data(proj))
	sl = list(shopping_list)
	for item in sl:
		for inv in (x for x in inventory if x.ingredient.id == item.id):
			# Subtract the buying count
			item.exact_buying_count -= inv.exact_buying_count
			#print('Subtracting ' + str(inv.amount) + inv.measurement + ' from ' + item.name)
			#inventory.remove(inv) # for optimization remove this element

			# Recalculate all the other properties
			# I most propably forgot something here
			item.exact_amount = item.exact_buying_count * item.buying_quantity
			if(item.calculation_measurement):
				item.exact_calculation_amount = item.exact_buying_count * item.calculation_quantity

			item.buying_count = math.ceil(item.exact_buying_count)
			item.effective_amount = item.buying_count * item.buying_quantity
			if(item.calculation_measurement):
				item.effective_calculation_amount = item.buying_count * item.calculation_quantity
			item.effective_price = item.buying_count * float(item.price)

	return [x for x in sl if x.exact_buying_count > 0.000001]

@login_required
def project_shopping_list(request):
	context = prepareContext(request)
	if('active_project' not in context):
		return redirect('cooking:projects')

	if('activate_inventory' in request.GET):
		request.session['inventory_active'] = True
	elif('deactivate_inventory' in request.GET):
		request.session['inventory_active'] = False
	elif('inventory_active' not in request.session):
		request.session['inventory_active'] = True

	if(request.session['inventory_active']):
		if('send_to_inventory' in request.GET):
			sl = project_shopping_list_data(context['active_project'])
			sl = subtract_inventory(context['active_project'], sl)
			for item in sl:
				add_to_inventory(context['active_project'], item)
		if('send_this_to_inventory' in request.GET):
			sl = project_shopping_list_data(context['active_project'])
			sl = subtract_inventory(context['active_project'], sl)
			ing = int(request.GET.get('item_id'))
			Ing = Ingredient.objects.get(id=ing)
			for item in sl:
				if(item.name == Ing.name):
					add_to_inventory(context['active_project'], item)

	context['shopping_list'] = project_shopping_list_data(context['active_project'])
	if(request.session['inventory_active']):
		context['shopping_list'] = subtract_inventory(context['active_project'], context['shopping_list'])
	#context['total_exact_price'] = context['shopping_list'].aggregate(tp=Sum('exact_price')).get('tp')
	context['total_effective_price'] = sum([float(x.effective_price) for x in context['shopping_list']])
	context['pagetitle'] = 'Shopping List'
	context['inventory_active'] = request.session['inventory_active']
	return render(request, 'listings/shopping_list.html', context)


@login_required
def project_shopping_list_csv(request):
	context = prepareContext(request)
	if('active_project' not in context):
		return redirect('cooking:projects')

	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="shoppinglist.csv"'

	writer = UnicodeWriter(response)
	writer.writerow(['First Use', 'Ingredient', 'Exact Amount 1', '', 'Exact Amount 2', '', 'Effective Amount 1', '', 'Effective Amount 2', '', 'Buying Count', 'Effective Price', 'Remarks'])
	if('inventory_active' not in request.session):
		request.session['inventory_active'] = True
	shoppinglist = project_shopping_list_data(context['active_project'])
	if(request.session['inventory_active']):
		shoppinglist = subtract_inventory(context['active_project'], shoppinglist)
	for item in shoppinglist:
		if(item.exact_amount > 0):
			writer.writerow([item.first_occurrence,
				item.name,
				item.exact_amount,
				conv_measurement(item.buying_measurement, item.exact_amount),
				item.exact_calculation_amount,
				conv_measurement(item.calculation_measurement, item.exact_calculation_amount),
				item.effective_amount,
				conv_measurement(item.buying_measurement, item.effective_amount),
				item.effective_calculation_amount,
				conv_measurement(item.calculation_measurement, item.effective_calculation_amount),
				item.buying_count,
				item.effective_price,
				item.remarks])

	return response
