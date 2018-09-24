"""
Login and logout views for the browsable API.

Add these to your root URLconf if you're using the browsable API and
your API requires authentication:

    urlpatterns = [
        ...
        url(r'^auth/', include('jet_django.deps.rest_framework.urls', namespace='jet_django.deps.rest_framework'))
    ]

In Django versions older than 1.9, the urls must be namespaced as 'jet_django.deps.rest_framework',
and you should make sure your authentication settings include `SessionAuthentication`.
"""
from __future__ import unicode_literals

from django.conf.urls import url
from django.contrib.auth import views

template_name = {'template_name': 'jet_django.deps.rest_framework/login.html'}

app_name = 'jet_django.deps.rest_framework'
urlpatterns = [
    url(r'^login/$', views.login, template_name, name='login'),
    url(r'^logout/$', views.logout, template_name, name='logout'),
]
