from django.conf.urls import patterns, url, include

import follow.views
urlpatterns = [
    url(r'^toggle/(?P<app>[^\/]+)/(?P<model>[^\/]+)/(?P<id>\d+)/$', follow.views.toggle, name='toggle'),
    url(r'^toggle/(?P<app>[^\/]+)/(?P<model>[^\/]+)/(?P<id>\d+)/$', follow.views.toggle, name='follow'),
    url(r'^toggle/(?P<app>[^\/]+)/(?P<model>[^\/]+)/(?P<id>\d+)/$', follow.views.toggle, name='unfollow'),
]
