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
router.register(r'comments', views.CommentModelViewSet)

projects_router = routers.NestedSimpleRouter(router, r'projects', lookup='project')
projects_router.register(r'components', views.ComponentViewSet)
projects_router.register(r'tasks', views.TaskViewSet)

users_router = routers.NestedSimpleRouter(router, r'users', lookup='TaskViewSet__owner11ProjectViewSet__members')
users_router.register(r'tasks', views.TaskViewSet)
users_router.register(r'projects', views.ProjectViewSet)

tasks_router = routers.NestedSimpleRouter(router, r'tasks', lookup='CommentModelViewSet__content_object')
tasks_router.register(r'comments', views.CommentModelViewSet)

urlpatterns = patterns('',
    url(r'^user/$', views.CurrentUserDetail.as_view()),
    
    url(r'^', include(router.urls)),
    url(r'^', include(projects_router.urls)),
    url(r'^', include(users_router.urls)),
    url(r'^', include(tasks_router.urls)),
)
