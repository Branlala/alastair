from django.conf.urls import include, url, patterns
from .meal import list_meals, new_meal, edit_meal, del_meal
from .meal_recipe import list_meal_receipe, meal_receipe_shopping_list

urlpatterns = [
	url(r'list$', list_meals, name='meals'),
	url(r'new$', new_meal, name='newmeal'),
	url(r'(?P<meal>[0-9]+)/$', list_meal_receipe, name='meals'),
	url(r'(?P<meal>[0-9]+)/edit/$', edit_meal, name='editmeal'),
	url(r'(?P<meal>[0-9]+)/del/$', del_meal, name='delmeal'),
	url(r'(?P<meal>[0-9]+)/(?P<receipe>[0-9]+)/$', meal_receipe_shopping_list, name='meals'),
]