from django.conf.urls import include, url, patterns
from .shopping_list import project_shopping_list, project_shopping_list_csv

urlpatterns = [
	url(r'^list$', project_shopping_list, name='shoppinglist'),
	url(r'^download.csv$', project_shopping_list_csv, name='shoppinglistcsv'),
]