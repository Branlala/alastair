from django.conf.urls import include, url, patterns
from .inventory import inventory

urlpatterns = [
	url(r'^list$', inventory, name='inventory'),
]