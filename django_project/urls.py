from django.conf.urls import patterns, url, include
from django_project import views

from rest_framework_nested import routers

router = routers.SimpleRouter()
router.register(r'projects', views.ProjectViewSet)
router.register(r'components', views.ComponentViewSet)
router.register(r'tasks', views.TaskViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'milestones', views.MilestoneModelViewSet)
router.register(r'groups', views.GroupViewSet)

projects_router = routers.NestedSimpleRouter(router, r'projects', lookup='projects')
projects_router.register(r'components', views.ComponentViewSet)
projects_router.register(r'tasks', views.TaskViewSet)

users_router = routers.NestedSimpleRouter(router, r'users', lookup='owners')
users_router.register(r'tasks', views.TaskViewSet)


urlpatterns = patterns('',
    url(r'^user/$', views.CurrentUserDetail.as_view()),
    
    url(r'^', include(router.urls)),
    url(r'^', include(projects_router.urls)),
    url(r'^', include(users_router.urls)),
)
