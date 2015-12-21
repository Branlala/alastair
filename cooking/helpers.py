import csv, codecs
import math
from django.core.urlresolvers import resolve
from django.db.models import F, ExpressionWrapper, FloatField, IntegerField, CharField, Case, When, Sum, Func, Min, Q
from django.template.defaulttags import register
from .models import Project, Ingredient, Inventory_Item, MEASUREMENTS, Receipe, Meal_Receipe

def validate_positive(value):
	if(value < 0):
		raise ValidationError('Please enter a positive value', code='negative-value')
	
def validate_greater_zero(value):
	if(value <= 0):
		raise ValidationError('Please enter a value greater than zero', code='not-zero')

MEASUREMENTS = (
	('ml', 'Milliliter'),
	('g', 'Gram'),
	('n', 'Piece'),
)

@register.filter(name='get_item')
def get_item(dictionary, key):
	return dictionary.get(key)

def conv_measurement(measurement, quantity):
	if(measurement == 'n'):
		if(quantity == 1):
			return 'piece'
		return 'pieces'
	return measurement

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