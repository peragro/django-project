from django.conf.urls import patterns, url, include
from django_project import views

from rest_framework_nested import routers

from rest_framework_extensions.routers import ExtendedSimpleRouter

router = ExtendedSimpleRouter()
projects_router = router.register(r'projects', views.ProjectViewSet)
router.register(r'components', views.ComponentViewSet)
tasks_router = router.register(r'tasks', views.TaskViewSet)
users_router = router.register(r'users', views.UserViewSet)
milestones_router = router.register(r'milestones', views.MilestoneModelViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'comments', views.CommentModelViewSet)
router.register(r'notifications', views.NotificationModelViewSet)

router.register(r'tasktypes', views.TaskTypeViewSet)
router.register(r'priorities', views.PriorityViewSet)
router.register(r'statuses', views.StatusViewSet)

projects_router.register(r'members', views.UserViewSet, base_name='projects-member', parents_query_lookups=['membership'])
projects_router.register(r'milestones', views.MilestoneModelViewSet, base_name='projects-milestone', parents_query_lookups=['project'])
projects_router.register(r'components', views.ComponentViewSet, base_name='projects-component', parents_query_lookups=['project'])
projects_router.register(r'tasks', views.TaskViewSet, base_name='projects-task', parents_query_lookups=['project'])
projects_router.register(r'tasktypes', views.TaskTypeViewSet, base_name='projects-tasktype', parents_query_lookups=['project'])
projects_router.register(r'priorities', views.PriorityViewSet, base_name='projects-priority', parents_query_lookups=['project'])
projects_router.register(r'statuses', views.StatusViewSet, base_name='projects-status', parents_query_lookups=['project'])

milestones_router.register(r'tasks', views.TaskViewSet, base_name='milestones-task', parents_query_lookups=['milestone'])

users_router.register(r'tasks', views.TaskViewSet, base_name='users-task', parents_query_lookups=['owner'])
users_router.register(r'projects', views.ProjectViewSet, base_name='users-project', parents_query_lookups=['members'])

#tasks_router = routers.NestedSimpleRouter(router, r'tasks', lookup='CommentModelViewSet__content_object')
tasks_router.register(r'comments', views.nested_viewset_with_genericfk(views.TaskViewSet, views.CommentModelViewSet), base_name='tasks-comment', parents_query_lookups=['object_pk'])

urlpatterns = patterns('',
    url(r'^user/$', views.CurrentUserDetail.as_view()),
    
    url(r'^', include(router.urls)),
    
    url(r'^chaining/', include('smart_selects.urls')),
)
