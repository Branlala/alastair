from django.conf.urls import include, url, patterns
from .ingredient import list_ingredients, ingredients_csv, edit_ingredient, del_ingredient, new_ingredient

urlpatterns = [
	url(r'^list$', list_ingredients, name='ingredients'),
	url(r'^download.csv$', ingredients_csv, name='ingredientscsv'),
	url(r'^(?P<ingredient>[0-9]+)/edit$', edit_ingredient, name='ingredients'),
	url(r'^(?P<ingredient>[0-9]+)/del$', del_ingredient, name='delingredient'),
	url(r'^new/$', new_ingredient, name='newingredient'),

]