"""alastair_cookie URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from .views import home, impressum, logout_view, tutorial
from .forms import MyLoginForm, MyPasswordChangeForm

urlpatterns = [
    url(r'^admin/', include(admin.site.urls), name='admin'),
    url(r'^home/$', home, name='home'),
    url(r'^help/$', tutorial, name='help'),
    url(r'^impressum/$', impressum, name='impressum'),
    url(r'^login/$', auth_views.login, {'authentication_form':MyLoginForm, 'extra_context':{'heading':'Login', 'pagetitle':'Login'}}),
    url(r'^password_change/$', auth_views.password_change, {'template_name':'registration/login.html', 'post_change_redirect':'/password_change/done/', 'password_change_form':MyPasswordChangeForm, 'extra_context':{'heading':'Change Password', 'pagetitle':'Change Password'}}),
    url(r'^logout/$', logout_view, name='logout'),
    url(r'^password_change/done/$', auth_views.password_change_done, {'template_name':'registration/login.html', 'extra_context':{'heading':'Password changed', 'message':'Your password was changed successfully!'}}),
    url('^', include('django.contrib.auth.urls')),
    url(r'^', include('cooking.urls', namespace='cooking'), name='cooking'),
    url(r'^$', home, name='home')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
