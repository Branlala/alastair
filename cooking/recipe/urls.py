from django.conf.urls import include, url, patterns
from .recipe import list_receipes, new_receipe, edit_receipe, del_receipe
from .recipe_ingredient import list_receipe_ingredient

urlpatterns = [
	url(r'list$', list_receipes, name='receipes'),
	url(r'new$', new_receipe, name='newreceipe'),
	url(r'(?P<active_recipe>[0-9]+)/edit$', edit_receipe, name='editreceipe'),
	url(r'(?P<active_recipe>[0-9]+)/del$', del_receipe, name='delreceipe'),
	url(r'(?P<active_recipe>[0-9]+)/$', list_receipe_ingredient, name='receipes'),

]