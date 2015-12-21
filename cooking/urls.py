from django.conf.urls import include, url, patterns


urlpatterns = [
	url(r'^project', include('cooking.project.urls')),
	#url(r'^meals/$', list_meals, name='meals'),
	#url(r'^meals/new$', new_meal, name='newmeal'),
	#url(r'^meal/(?P<meal>[0-9]+)/$', list_meal_receipe, name='meals'),
	#url(r'^meal/(?P<meal>[0-9]+)/edit/$', edit_meal, name='editmeal'),
	#url(r'^meal/(?P<meal>[0-9]+)/del/$', del_meal, name='delmeal'),
	#url(r'^meal/(?P<meal>[0-9]+)/(?P<receipe>[0-9]+)/$', meal_receipe_shopping_list, name='meals'),
	#url(r'^shopping_list/$', project_shopping_list, name='shoppinglist'),
	#url(r'^shopping_list/download.csv$', project_shopping_list_csv, name='shoppinglistcsv'),
	#url(r'^inventory/$', inventory, name='inventory'),
	#url(r'^propose_receipes/$', propose_receipes, name='proposereceipes'),
	#url(r'^receipes/$', list_receipes, name='receipes'),
	#url(r'^receipes/new$', new_receipe, name='newreceipe'),
	#url(r'^receipe/(?P<active_receipe>[0-9]+)/$', list_receipe_ingredient, name='receipes'),
	#url(r'^receipe/(?P<active_receipe>[0-9]+)/edit$', edit_receipe, name='editreceipe'),
	#url(r'^receipe/(?P<active_receipe>[0-9]+)/del$', del_receipe, name='delreceipe'),
	#url(r'^ingredients/$', list_ingredients, name='ingredients'),
	#url(r'^ingredients/download.csv$', ingredients_csv, name='ingredientscsv'),
	#url(r'^ingredient/(?P<ingredient>[0-9]+)/edit$', edit_ingredient, name='ingredients'),
	#url(r'^ingredient/(?P<ingredient>[0-9]+)/del$', del_ingredient, name='delingredient'),
	#url(r'^ingredients/new/$', new_ingredient, name='newingredient'),
	#url(r'^allergens/$', list_allergens, name='allergens'),
]
