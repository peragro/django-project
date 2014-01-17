from django_project import views

from rest_framework import routers
router = routers.DefaultRouter()

router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)

router.register(r'projects', views.ProjectViewSet)
router.register(r'milestones', views.MilestoneModelViewSet)
router.register(r'tasks', views.TaskViewSet)
