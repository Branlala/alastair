from django.conf.urls import include, url, patterns
from .views import hello, list_projects, new_project, del_project, edit_project, list_meals, edit_meal, del_meal, new_meal, list_meal_receipe, meal_receipe_shopping_list, project_shopping_list, inventory
from .view_statics import list_receipes, edit_receipe, new_receipe, del_receipe, list_receipe_ingredient, list_ingredients,  edit_ingredient, new_ingredient, del_ingredient, list_allergens
from .csv_views import project_shopping_list_csv, ingredients_csv

urlpatterns = [
    url(r'^hello/$', hello, name='hello'),
    url(r'^projects/$', list_projects, name='projects'),
    url(r'^projects/new$', new_project, name='newproject'),
	url(r'^project/(?P<project>[0-9]+)/edit/$', edit_project, name='editproject'),
	url(r'^project/(?P<project>[0-9]+)/del/$', del_project, name='delproject'),
	url(r'^meals/$', list_meals, name='meals'),
	url(r'^meals/new$', new_meal, name='newmeal'),
	url(r'^meal/(?P<meal>[0-9]+)/$', list_meal_receipe, name='meals'),
	url(r'^meal/(?P<meal>[0-9]+)/edit/$', edit_meal, name='editmeal'),
	url(r'^meal/(?P<meal>[0-9]+)/del/$', del_meal, name='delmeal'),
	url(r'^meal/(?P<meal>[0-9]+)/(?P<receipe>[0-9]+)/$', meal_receipe_shopping_list, name='meals'),
    url(r'^shopping_list/$', project_shopping_list, name='shoppinglist'),
    url(r'^shopping_list/download.csv$', project_shopping_list_csv, name='shoppinglistcsv'),
    url(r'^inventory/$', inventory, name='inventory'),
    url(r'^receipes/$', list_receipes, name='receipes'),
    url(r'^receipes/new$', new_receipe, name='newreceipe'),
    url(r'^receipe/(?P<active_receipe>[0-9]+)/$', list_receipe_ingredient, name='receipes'),
    url(r'^receipe/(?P<active_receipe>[0-9]+)/edit$', edit_receipe, name='editreceipe'),
    url(r'^receipe/(?P<active_receipe>[0-9]+)/del$', del_receipe, name='delreceipe'),
    url(r'^ingredients/$', list_ingredients, name='ingredients'),
    url(r'^ingredients/download.csv$', ingredients_csv, name='ingredientscsv'),
    url(r'^ingredient/(?P<ingredient>[0-9]+)/edit$', edit_ingredient, name='ingredients'),
	url(r'^ingredient/(?P<ingredient>[0-9]+)/del$', del_ingredient, name='delingredient'),
    url(r'^ingredients/new/$', new_ingredient, name='newingredient'),
    url(r'^allergens/$', list_allergens, name='allergens'),
]
