from django.conf.urls import include, url, patterns
from .inventory import inventory

urlpatterns = [
	url(r'^inventory/$', inventory, name='inventory'),
]