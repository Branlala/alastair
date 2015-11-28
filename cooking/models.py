
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum
from django.utils.encoding import python_2_unicode_compatible
import decimal

def validate_positive(value):
	if(value < 0):
		raise ValidationError('Please enter a positive value', code='negative-value')

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
	buying_quantity = models.FloatField(validators=[validate_positive])
	buying_measurement = models.CharField(max_length=2, choices=MEASUREMENTS)
	calculation_quantity = models.FloatField(blank=True, null=True, validators=[validate_positive])
	calculation_measurement = models.CharField(max_length=2, choices=MEASUREMENTS, blank=True, null=True)	
	price = models.DecimalField(max_digits=8, decimal_places=2, validators=[validate_positive])
	cheapest_store = models.CharField(max_length=256, blank=True)
	remarks = models.CharField(max_length=256, blank=True)
	allergens = models.ManyToManyField(Allergen, blank=True)
	cooked_weight = models.FloatField(default=0, validators=[validate_positive])

	def __str__(self):
		return self.name
	
	class Meta:
		ordering = ['name']
	
@python_2_unicode_compatible
class Receipe(models.Model):
	name = models.CharField(max_length=256)
	default_person_count = models.IntegerField(default=1, validators=[MinValueValidator(1)])
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
	price = models.FloatField(validators=[validate_positive])
	
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
	amount = models.FloatField(validators=[validate_positive])
	measurement = models.CharField(max_length=2, choices=MEASUREMENTS)
	remarks = models.CharField(max_length=256, blank=True)

	
	def __str__(self):
		return self.ingredient.name
	
	class Meta:
		ordering = ['ingredient']
		unique_together = ('project', 'ingredient',)
		
		
@python_2_unicode_compatible
class Receipe_Ingredient(models.Model):
	receipe = models.ForeignKey(Receipe)
	ingredient = models.ForeignKey(Ingredient)
	amount = models.FloatField(validators=[validate_positive])
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
	person_count = models.IntegerField(validators=[validate_positive])
	remarks = models.CharField(max_length=256, blank=True)
	
	def __str__(self):
		return u'%s - %s' % (self.meal.name, self.receipe.name)
	
	class Meta:
		ordering = ['meal', 'receipe']
