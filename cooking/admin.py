#from django.contrib import admin
#from cooking.form_statics import Receipe_IngredientForm, IngredientForm

#from cooking.models import Allergen, Ingredient, Receipe, Meal, Project, Receipe_Ingredient, Meal_Receipe

#class Receipe_IngredientAdmin(admin.ModelAdmin):
	#list_display = ('receipe', 'ingredient', 'amount', 'measurement')
	#form = Receipe_IngredientForm
	
#class Meal_ReceipeAdmin(admin.ModelAdmin):
	#list_display = ('meal', 'receipe', 'person_count')

#class IngredientAdmin(admin.ModelAdmin):
	#list_display = ('name', 'price')
	#search_fields = ('name',)
	#filter_horizontal = ('allergens',)
	#form = IngredientForm
	
#class ReceipeAdmin(admin.ModelAdmin):
	#list_display = ('name', 'default_person_count')
	#search_fields = ('name',)
	
#class MealAdmin(admin.ModelAdmin):
	#list_display = ('project', 'time', 'name')
	#search_fields = ('name',)

#admin.site.register(Allergen)
#admin.site.register(Ingredient, IngredientAdmin)
#admin.site.register(Receipe, ReceipeAdmin)
#admin.site.register(Meal, MealAdmin)
#admin.site.register(Project)
#admin.site.register(Receipe_Ingredient, Receipe_IngredientAdmin)
#admin.site.register(Meal_Receipe, Meal_ReceipeAdmin)