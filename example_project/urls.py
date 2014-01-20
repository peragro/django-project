from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import notifications


from django_project.urls import router


urlpatterns = patterns('',
    # Examples:
    #url(r'^$', 'django_project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-token-auth/', 'rest_framework.authtoken.views.obtain_auth_token'),

    url(r'^admin/', include(admin.site.urls)),
    
)

urlpatterns = patterns('',
    ('^inbox/notifications/', include(notifications.urls)),
    url(r'^toggle/(?P<app>[^\/]+)/(?P<model>[^\/]+)/(?P<id>\d+)/$', 'follow.views.toggle', name='toggle'),
    url(r'^toggle/(?P<app>[^\/]+)/(?P<model>[^\/]+)/(?P<id>\d+)/$', 'follow.views.toggle', name='follow'),
    url(r'^toggle/(?P<app>[^\/]+)/(?P<model>[^\/]+)/(?P<id>\d+)/$', 'follow.views.toggle', name='unfollow'),
)
