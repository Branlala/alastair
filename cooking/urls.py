from django.conf.urls import include, url, patterns

urlpatterns = [
	url(r'^project/', include('cooking.project.urls')),
	url(r'^meal/', include('cooking.meal.urls')),
	url(r'^shopping_list/', include('cooking.shopping_list.urls')),
	url(r'^inventory/', include('cooking.inventory.urls')),
	url(r'^recipe/', include('cooking.recipe.urls')),
	url(r'^ingredient/', include('cooking.ingredient.urls')),
	url(r'^allergen/', include('cooking.allergen.urls')),
]
