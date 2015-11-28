import csv, codecs
import math
from django.core.urlresolvers import resolve
from django.db.models import F, ExpressionWrapper, FloatField, IntegerField, CharField, Case, When, Sum, Func, Min, Q
from django.template.defaulttags import register
from .models import Project, Ingredient, Inventory_Item, MEASUREMENTS

@register.filter(name='get_item')
def get_item(dictionary, key):
	return dictionary.get(key)

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

def meal_shopping_list(meal, receipe):
	return Ingredient.objects.filter(receipe=receipe, receipe__meal=meal).annotate(
		# Copy ri.measurement for easier access
		measurement=F('receipe_ingredient__measurement'),
		# Also copy ri.remarks for easier access
		mr_remarks=F('receipe_ingredient__remarks'),
		# Exact price = (mr.person_count / r.default_person_count) * i.price
		exact_price=ExpressionWrapper((F('receipe__meal_receipe__person_count') / F('receipe__default_person_count')) * F('price'), output_field=FloatField()),
		
		exact_amount=Case(
			When(buying_measurement=F('receipe_ingredient__measurement'),
				 then=(F('receipe_ingredient__amount') / F('receipe__default_person_count')) * F('receipe__meal_receipe__person_count')),
			When(calculation_measurement=F('receipe_ingredient__measurement'),
				 then=(((F('receipe_ingredient__amount') / F('calculation_quantity')) * F('buying_quantity')) / F('receipe__default_person_count')) * F('receipe__meal_receipe__person_count')),
			default=0,
			output_field=FloatField()),
		exact_calculation_amount=Case(
			When(calculation_measurement__isnull=True,
				 then=None),
			When(buying_measurement=F('receipe_ingredient__measurement'),
				 then=(((F('receipe_ingredient__amount') / F('buying_quantity')) * F('calculation_quantity')) / F('receipe__default_person_count')) * F('receipe__meal_receipe__person_count')),
			When(calculation_measurement=F('receipe_ingredient__measurement'),
				 then=(F('receipe_ingredient__amount') / F('receipe__default_person_count')) * F('receipe__meal_receipe__person_count')),
			default=None,
			output_field=FloatField()),
		)
	

	
def project_shopping_list_data(proj):
	#if(inventory_active):
		## qs1 is all the shopping list items that have an item in inventory (and already the amount subtracted)
		## qs2 is all the shopping list items without an item in inventory
		#qs1 = Ingredient.objects.filter(receipe__meal__project=proj, receipe__meal__project__inventory_item__ingredient=F('pk')).annotate(
			## Copy ri.measurement for easier access
			#measurement=F('receipe_ingredient__measurement'),
			## Also copy ri.remarks for easier access
			#mr_remarks=F('receipe_ingredient__remarks'),
			## Exact price = (mr.person_count / r.default_person_count) * i.price
			#exact_price_tmp=ExpressionWrapper((F('receipe__meal_receipe__person_count') / F('receipe__default_person_count')) * F('price'), output_field=FloatField()),
			
			#exact_amount_tmp=Case(
				#When(buying_measurement=F('receipe_ingredient__measurement'),
					#then=(F('receipe_ingredient__amount') / F('receipe__default_person_count')) * F('receipe__meal_receipe__person_count')),
				#When(calculation_measurement=F('receipe_ingredient__measurement'),
					#then=(((F('receipe_ingredient__amount') / F('calculation_quantity')) * F('buying_quantity')) / F('receipe__default_person_count')) * F('receipe__meal_receipe__person_count')),
				#default=0,
				#output_field=FloatField()),
			#exact_calculation_amount_tmp=Case(
				#When(calculation_measurement__isnull=True,
					#then=None),
				#When(buying_measurement=F('receipe_ingredient__measurement'),
					#then=(((F('receipe_ingredient__amount') / F('buying_quantity')) * F('calculation_quantity')) / F('receipe__default_person_count')) * F('receipe__meal_receipe__person_count')),
				#When(calculation_measurement=F('receipe_ingredient__measurement'),
					#then=(F('receipe_ingredient__amount') / F('receipe__default_person_count')) * F('receipe__meal_receipe__person_count')),
				#default=None,
				#output_field=FloatField()),
		#).annotate(
			#exact_amount_tmp_tmp=Sum('exact_amount_tmp') - Case(
														#When(buying_measurement=F('receipe__meal__project__inventory_item__measurement'), then=F('receipe__meal__project__inventory_item__amount')),
														#When(calculation_measurement=F('receipe__meal__project__inventory_item__measurement'), then=(F('receipe__meal__project__inventory_item__amount') / F('calculation_quantity')) * F('buying_quantity')),
														#default=0,
														#output_field=FloatField()),
			#first_occurrence=Min('receipe__meal__time'),
		## Due to a bug in django this does not work:
		## https://code.djangoproject.com/ticket/18378
		##).filter(
			##exact_amount__gt=0,
		## As a fix we need this and a loop over all shopping list items
		## Fuck floating precision!
		#).annotate(
			#exact_amount=Case(When(exact_amount_tmp_tmp__gt=0.0000001, then=F('exact_amount_tmp_tmp')),
							  #default=0,
							  #output_field=FloatField()),
		#).annotate(
			#exact_calculation_amount=Case(When(calculation_measurement__isnull=False, then=F('exact_amount') / F('buying_quantity') * F('calculation_quantity')),
										#default=None,
										#output_field=FloatField()),
			#buying_count=Func((F('exact_amount') / F('buying_quantity')) + 0.5, function='ROUND'),
		#).annotate(
			#effective_amount=F('buying_count') * F('buying_quantity'),
			#effective_calculation_amount=F('buying_count') * F('calculation_quantity'),
			#effective_price=ExpressionWrapper(F('buying_count') * F('price'), output_field=FloatField()),
		#).values('first_occurrence', 'name', 'id', 'buying_measurement', 'buying_quantity', 'calculation_measurement', 'calculation_quantity', 'exact_amount', 'exact_calculation_amount', 'effective_amount', 'effective_calculation_amount', 'remarks', 'effective_price', 'buying_count', 'price')
		
		#qs2 = Ingredient.objects.filter(receipe__meal__project__id=2).annotate(
			#matchcount=Case(
				#When(receipe__meal__project__inventory_item__ingredient=F('pk'), then=1),
				#default=0, 
				#output_field=IntegerField()
				#)
		#).annotate(invcount=Sum('matchcount')).order_by('name').filter(invcount=0).annotate(
			## Copy ri.measurement for easier access
			#measurement=F('receipe_ingredient__measurement'),
			## Also copy ri.remarks for easier access
			#mr_remarks=F('receipe_ingredient__remarks'),
			## Exact price = (mr.person_count / r.default_person_count) * i.price
			#exact_price_tmp=ExpressionWrapper((F('receipe__meal_receipe__person_count') / F('receipe__default_person_count')) * F('price'), output_field=FloatField()),
			
			#exact_amount_tmp=Case(
				#When(buying_measurement=F('receipe_ingredient__measurement'),
					#then=(F('receipe_ingredient__amount') / F('receipe__default_person_count')) * F('receipe__meal_receipe__person_count')),
				#When(calculation_measurement=F('receipe_ingredient__measurement'),
					#then=(((F('receipe_ingredient__amount') / F('calculation_quantity')) * F('buying_quantity')) / F('receipe__default_person_count')) * F('receipe__meal_receipe__person_count')),
				#default=0,
				#output_field=FloatField()),
			#exact_calculation_amount_tmp=Case(
				#When(calculation_measurement__isnull=True,
					#then=None),
				#When(buying_measurement=F('receipe_ingredient__measurement'),
					#then=(((F('receipe_ingredient__amount') / F('buying_quantity')) * F('calculation_quantity')) / F('receipe__default_person_count')) * F('receipe__meal_receipe__person_count')),
				#When(calculation_measurement=F('receipe_ingredient__measurement'),
					#then=(F('receipe_ingredient__amount') / F('receipe__default_person_count')) * F('receipe__meal_receipe__person_count')),
				#default=None,
				#output_field=FloatField()),
		#).annotate(
			#exact_amount_tmp_tmp=Sum('exact_amount_tmp'),
			#first_occurrence=Min('receipe__meal__time'),
		## Due to a bug in django this does not work:
		## https://code.djangoproject.com/ticket/18378
		##).filter(
			##exact_amount__gt=0,
		## As a fix we need this and a loop over all shopping list items
		## Fuck floating precision!
		#).annotate(
			#exact_amount=Case(When(exact_amount_tmp_tmp__gt=0.0000001, then=F('exact_amount_tmp_tmp')),
							  #default=0,
							  #output_field=FloatField()),
		#).annotate(
			#exact_calculation_amount=Case(When(calculation_measurement__isnull=False, then=F('exact_amount') / F('buying_quantity') * F('calculation_quantity')),
										#default=None,
										#output_field=FloatField()),
			#buying_count=Func((F('exact_amount') / F('buying_quantity')) + 0.5, function='ROUND'),
		#).annotate(
			#effective_amount=F('buying_count') * F('buying_quantity'),
			#effective_calculation_amount=F('buying_count') * F('calculation_quantity'),
			#effective_price=ExpressionWrapper(F('buying_count') * F('price'), output_field=FloatField()),
		#).values('first_occurrence', 'name', 'id', 'buying_measurement', 'buying_quantity', 'calculation_measurement', 'calculation_quantity', 'exact_amount', 'exact_calculation_amount', 'effective_amount', 'effective_calculation_amount', 'remarks', 'effective_price', 'buying_count', 'price')
		#return Ingredient.objects.raw('(' + str(qs1.query) + ') UNION (' + str(qs2.query) + ') ORDER BY name')
	#else:
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
			item.effective_price = item.buying_count * item.price
				
	return [x for x in sl if x.exact_buying_count > 0.000001]

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
	

def prepareContext(request):
	context = {}
	if('activate_project' in request.GET):
		try:
			request.session['active_project']=int(request.GET.get('activate_project'))
		except:
			try:
				del request.session['active_project']
			except:
				pass
	
	try:
		context['active_project'] = Project.objects.get(id=request.session['active_project'])
	except:
		pass
	context['active_page'] = resolve(request.path_info).url_name
	context['pagetitle'] = context['active_page']
	return context

## Ugly thing: if we can import the python2-module, define stuff...
try:
	import cStringIO
		
	def _smallhelpforunicode(arg):
		if(arg == None):
			return ''
		return unicode(arg)


	class UnicodeWriter:
		"""
		A CSV writer which will write rows to CSV file "f",
		which is encoded in the given encoding.
		"""

		def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
			# Redirect output to a queue
			self.queue = cStringIO.StringIO()
			self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
			self.stream = f
			self.encoder = codecs.getincrementalencoder(encoding)()

		def writerow(self, row):
			self.writer.writerow([_smallhelpforunicode(s).encode("utf-8") for s in row])
			# Fetch UTF-8 output from the queue ...
			data = self.queue.getvalue()
			data = data.decode("utf-8")
			# ... and reencode it into the target encoding
			data = self.encoder.encode(data)
			# write to the target stream
			self.stream.write(data)
			# empty queue
			self.queue.truncate(0)

		def writerows(self, rows):
			for row in rows:
				self.writerow(row)
except:
	pass