import csv, codecs
from django.core.urlresolvers import resolve
from django.db.models import F, ExpressionWrapper, FloatField, CharField, Case, When, Sum, Func, Min, Q
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
	
def project_shopping_list_data(proj, inventory_active):
	if(inventory_active):
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
			exact_amount_tmp_tmp=Sum('exact_amount_tmp') - Case(When(inventory_item__isnull=True, then=0),
														When(buying_measurement=F('inventory_item__measurement'), then=F('inventory_item__amount')),
														When(calculation_measurement=F('inventory_item__measurement'), then=(F('inventory_item__amount') / F('calculation_quantity')) * F('buying_quantity')),
														default=0,
														output_field=FloatField()),
			first_occurrence=Min('receipe__meal__time'),
		# Due to a bug in django this does not work:
		# https://code.djangoproject.com/ticket/18378
		#).filter(
			#exact_amount__gt=0,
		# As a fix we need this and a loop over all shopping list items
		# Fuck floating precision!
		).annotate(
			exact_amount=Case(When(exact_amount_tmp_tmp__gt=0.0000001, then=F('exact_amount_tmp_tmp')),
							  default=0,
							  output_field=FloatField()),
		).annotate(
			exact_calculation_amount=Case(When(calculation_measurement__isnull=False, then=F('exact_amount') / F('buying_quantity') * F('calculation_quantity')),
										default=None,
										output_field=FloatField()),
			buying_count=Func((F('exact_amount') / F('buying_quantity')) + 0.5, function='ROUND'),
		).annotate(
			effective_amount=F('buying_count') * F('buying_quantity'),
			effective_calculation_amount=F('buying_count') * F('calculation_quantity'),
			effective_price=ExpressionWrapper(F('buying_count') * F('price'), output_field=FloatField()),
		)
	else:
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
			buying_count=Func((F('exact_amount') / F('buying_quantity')) + 0.5, function='ROUND'),
		).annotate(
			effective_amount=F('buying_count') * F('buying_quantity'),
			effective_calculation_amount=F('buying_count') * F('calculation_quantity'),
			effective_price=ExpressionWrapper(F('buying_count') * F('price'), output_field=FloatField()),
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