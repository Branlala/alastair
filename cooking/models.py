

from django.db import models
from django.db.models import Sum
from django.utils.encoding import python_2_unicode_compatible
import decimal


MEASUREMENTS = (
	('ml', 'Milliliter'),
	('g', 'Gram'),
	('n', 'Piece'),
)

@python_2_unicode_compatible
class Allergen(models.Model):
	name = models.CharField(max_length=256)
	def __str__(self):
		return self.name
	
	class Meta:
		ordering = ['name']
	
@python_2_unicode_compatible
class Ingredient(models.Model):
	name = models.CharField(max_length=256)
	buying_quantity = models.FloatField()
	buying_measurement = models.CharField(max_length=2, choices=MEASUREMENTS)
	calculation_quantity = models.FloatField(blank=True, null=True)
	calculation_measurement = models.CharField(max_length=2, choices=MEASUREMENTS, blank=True, null=True)
	price = models.DecimalField(max_digits=8, decimal_places=2)
	cheapest_store = models.CharField(max_length=256, blank=True)
	remarks = models.CharField(max_length=256, blank=True)
	allergens = models.ManyToManyField(Allergen, blank=True)
	
	def __str__(self):
		return self.name
	
	class Meta:
		ordering = ['name']
	
@python_2_unicode_compatible
class Receipe(models.Model):
	name = models.CharField(max_length=256)
	default_person_count = models.IntegerField(default=1)
	instructions = models.TextField()
	ingredients = models.ManyToManyField(Ingredient, through='Receipe_Ingredient')
	def __str__(self):
		return self.name
	
	class Meta:
		ordering = ['name']
		
@python_2_unicode_compatible
class Project(models.Model):
	name = models.CharField(max_length=256)
	start_date = models.DateField(blank=True, null=True)
	end_date = models.DateField(blank=True, null=True)
	def __str__(self):
		return self.name
	
	class Meta:
		ordering = ['start_date', 'name']
		
@python_2_unicode_compatible
class Project_Readonly(models.Model):
	name = models.CharField(max_length=256)
	start_date = models.DateField(blank=True, null=True)
	end_date = models.DateField(blank=True, null=True)
	price = models.FloatField()
	
	def __str__(self):
		return self.name
	
	class Meta:
		managed = False
		db_table = 'cooking_project_readonly'
		default_permissions = ()
		ordering = ['start_date', 'name']
	
	
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
		
		
@python_2_unicode_compatible
class Inventory_Item(models.Model):
	project = models.ForeignKey(Project)
	ingredient = models.ForeignKey(Ingredient)
	amount = models.FloatField()
	measurement = models.CharField(max_length=2, choices=MEASUREMENTS)
	remarks = models.CharField(max_length=256, blank=True)
	
	def exact_price(self):
		if(self.measurement == self.ingredient.calculation_measurement):
			return decimal.Decimal(self.amount / self.ingredient.calculation_quantity) * self.ingredient.price
		else:
			return decimal.Decimal(self.amount / self.ingredient.buying_quantity) * self.ingredient.price
	
	def __str__(self):
		return self.ingredient.name
	
	class Meta:
		ordering = ['ingredient']
		unique_together = ('project', 'ingredient',)
		
		
@python_2_unicode_compatible
class Receipe_Ingredient(models.Model):
	receipe = models.ForeignKey(Receipe)
	ingredient = models.ForeignKey(Ingredient)
	amount = models.FloatField()
	measurement = models.CharField(max_length=2, choices=MEASUREMENTS)
	remarks = models.CharField(max_length=256, blank=True)
	
	def __str__(self):
		return u'%s - %s' % (self.receipe.name, self.ingredient.name)
	
	class Meta:
		ordering = ['receipe', 'ingredient']
	
	
@python_2_unicode_compatible
class Meal_Receipe(models.Model):
	meal = models.ForeignKey(Meal)
	receipe = models.ForeignKey(Receipe)
	person_count = models.IntegerField()
	remarks = models.CharField(max_length=256, blank=True)
	
	def __str__(self):
		return u'%s - %s' % (self.meal.name, self.receipe.name)
	
	class Meta:
		ordering = ['meal', 'receipe']

@python_2_unicode_compatible
class Meal_Receipe_Shopping_List(models.Model):
	project_id = models.IntegerField(db_column='proj_id')
	meal_id = models.IntegerField()
	receipe_id = models.IntegerField()
	ing_id = models.IntegerField()
	name = models.CharField(max_length=256)
	exact_amount = models.FloatField()
	exact_price = models.FloatField()
	effective_amount = models.FloatField()
	buying_count = models.FloatField()
	buying_quantity = models.FloatField()
	buying_measurement = models.CharField(max_length=2, choices=MEASUREMENTS)
	effective_price = models.FloatField()
	remarks = models.CharField(max_length=256)
	ing_remarks = models.CharField(max_length=256)
	
	def __str__(self):
		return self.name
	
	class Meta:
		ordering = ['project_id', 'meal_id', 'receipe_id', 'name']
		managed = False
		db_table = 'cooking_meal_receipe_pricelist'
		default_permissions = ()

@python_2_unicode_compatible
class Project_Shopping_List(models.Model):
	project_id = models.IntegerField(db_column='project_id')
	ing_id = models.IntegerField(primary_key=True)
	name = models.CharField(max_length=256)
	exact_amount = models.FloatField()
	exact_price = models.FloatField()
	effective_amount = models.FloatField()
	buying_count = models.FloatField()
	buying_quantity = models.FloatField()
	buying_measurement = models.CharField(max_length=2, choices=MEASUREMENTS)
	calculation_quantity = models.FloatField(null=True)
	calculation_measurement = models.CharField(max_length=2, choices=MEASUREMENTS, null=True)
	effective_price = models.FloatField()
	remarks = models.CharField(max_length=256)
	first_occurrence = models.DateTimeField(blank=True, null=True)
	
	def effective_calculation_amount(self):
		if(self.calculation_measurement):
			return self.buying_count * self.calculation_quantity
		else:
			return None
		
	def exact_calculation_amount(self):
		if(self.calculation_measurement):
			return (self.exact_amount / self.buying_quantity) * self.calculation_quantity
		else:
			return None
	
	def __str__(self):
		return self.name
	
	class Meta:
		ordering = ['project_id', 'first_occurrence', 'name']
		managed = False
		db_table = 'cooking_project_pricelist'
		default_permissions = ()

@python_2_unicode_compatible
class Project_Shopping_List_Invsub(models.Model):
	project_id = models.IntegerField(db_column='project_id')
	ing_id = models.IntegerField(primary_key=True)
	name = models.CharField(max_length=256)
	exact_amount = models.FloatField()
	exact_price = models.FloatField()
	effective_amount = models.FloatField()
	buying_count = models.FloatField()
	buying_quantity = models.FloatField()
	buying_measurement = models.CharField(max_length=2, choices=MEASUREMENTS)
	calculation_quantity = models.FloatField(null=True)
	calculation_measurement = models.CharField(max_length=2, choices=MEASUREMENTS, null=True)
	effective_price = models.FloatField()
	remarks = models.CharField(max_length=256)
	first_occurrence = models.DateTimeField(blank=True, null=True)
	
	def effective_calculation_amount(self):
		if(self.calculation_measurement):
			return self.buying_count * self.calculation_quantity
		else:
			return None
		
	def exact_calculation_amount(self):
		if(self.calculation_measurement):
			return (self.exact_amount / self.buying_quantity) * self.calculation_quantity
		else:
			return None
	
	def __str__(self):
		return self.name
	
	class Meta:
		ordering = ['project_id', 'first_occurrence', 'name']
		managed = False
		db_table = 'cooking_project_pricelist_invsub'
		default_permissions = ()