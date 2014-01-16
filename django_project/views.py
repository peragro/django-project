import os
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType

from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action, link

from notifications.models import Notification

from follow.models import Follow

from django_project.serializers import UserSerializer, GroupSerializer
from django_project.serializers import ProjectSerializer, TaskSerializer, NotificationSerializer, UserSerializer

from django_project.models import Project, Task

class FollowingModelViewSet(viewsets.ModelViewSet):
    @link(permission_classes=[])
    def followers(self, request, pk):    
        obj = self.queryset.get(id=int(pk))
        
        users = User.objects.filter(id__in=Follow.objects.get_follows(obj).values_list('user'))
        
        serializer = UserSerializer(users)

        return Response(serializer.data)
        
    @link(permission_classes=[])
    def activity(self, request, pk):
        print("FollowingModelViewSet: ", pk)
        obj = self.queryset.get(id=int(pk))
        
        kwargs = {}
        kwargs['public'] = True
        if self.notifications_field=='recipient': 
            kwargs['recipient'] = obj
        else:
            kwargs[self.notifications_field+'_content_type'] = ContentType.objects.get_for_model(obj)
            kwargs[self.notifications_field+'_object_id'] = obj.id
        
        notifications = Notification.objects.filter(**kwargs)

        serializer = NotificationSerializer(notifications)

        return Response(serializer.data)


class UserViewSet(FollowingModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    notifications_field = 'recipient'
    
    @link(permission_classes=[])
    def tasks(self, request, pk):    
        user = self.queryset.get(id=int(pk))
        
        tasks = user.owned_tasks.filter(status__is_resolved=False)
        
        serializer = TaskSerializer(tasks)

        return Response(serializer.data)


class GroupViewSet(FollowingModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class ProjectViewSet(FollowingModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    notifications_field = 'target'
    
    @link(permission_classes=[])
    def tasks(self, request, pk):  
        print(self.kwargs)
        project = self.queryset.get(id=int(pk))
        
        tasks = project.task_set.filter(status__is_resolved=False)
        
        serializer = TaskSerializer(tasks)

        return Response(serializer.data)


class TaskViewSet(FollowingModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    notifications_field = 'action_object'

    
