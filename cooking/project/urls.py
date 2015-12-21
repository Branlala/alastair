from django.conf.urls import include, url, patterns
from .project import list_projects, new_project, edit_project, del_project

urlpatterns = [
	url(r'list$', list_projects, name='projects'),
	url(r'new$', new_project, name='newproject'),
	url(r'(?P<project>[0-9]+)/edit/$', edit_project, name='editproject'),
	url(r'(?P<project>[0-9]+)/del/$', del_project, name='delproject'),
]