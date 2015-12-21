from django.conf.urls import include, url, patterns
from .allergen import list_allergens

urlpatterns = [
	url(r'list$', list_allergens, name='allergens'),

]