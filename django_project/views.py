import os
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType

from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action, link
from rest_framework import status

from rest_framework.permissions import IsAuthenticated

from notifications.models import Notification

from follow.models import Follow
import follow

from django_project.serializers import UserSerializer, GroupSerializer
from django_project.serializers import ProjectSerializer, MilestoneSerializer, TaskSerializer, NotificationSerializer, UserSerializer

from django_project.models import Project, Task, Milestone

from django_project import signals

class FollowingModelViewSet(viewsets.ModelViewSet):
    @action(methods=['POST', 'DELETE'], permission_classes=[IsAuthenticated])
    def follow(self, request, pk):  
        obj = self.queryset.get(id=int(pk))
        
        #follow, created = Follow.objects.get_or_create(request.user, obj)
        can_change_follow = True
        if hasattr(self, 'can_change_follow'):
            can_change_follow = self.can_change_follow(request.user, obj)
        
        if can_change_follow:
            if request.method == 'DELETE':
                if Follow.objects.is_following(request.user, obj):
                    fol = follow.utils.unfollow(request.user, obj)
                    signals.unfollow.send(FollowingModelViewSet, follower=request.user, followee=obj)
                return Response(status=status.HTTP_205_RESET_CONTENT)
            elif request.method == 'POST':
                if not Follow.objects.is_following(request.user, obj):
                    fol = follow.utils.follow(request.user, obj)
                    signals.follow.send(FollowingModelViewSet, follower=request.user, followee=obj)
                return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
            
    
    @link()
    def followers(self, request, pk):    
        obj = self.queryset.get(id=int(pk))
        
        users = User.objects.filter(id__in=Follow.objects.get_follows(obj).values_list('user'))
        
        serializer = UserSerializer(users)

        return Response(serializer.data)
        
    @link()
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
            
        if self.notifications_field=='target':
            kwargs['recipient'] = obj.author
        
        notifications = Notification.objects.filter(**kwargs)

        serializer = NotificationSerializer(notifications)

        return Response(serializer.data)


class MilestoneModelViewSet(viewsets.ModelViewSet):
    queryset = Milestone.objects.all()
    serializer_class = MilestoneSerializer
    

class UserViewSet(FollowingModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    notifications_field = 'recipient'
    
    def can_change_follow(self, user, obj):
        # Don't allow users to follow themselfs
        return user.id != obj.id
    
    @link(permission_classes=[])
    def tasks(self, request, pk):    
        user = self.queryset.get(id=int(pk))
        
        tasks = user.owned_tasks.filter(status__is_resolved=False)
        
        serializer = TaskSerializer(tasks)

        return Response(serializer.data)
    
    @link(permission_classes=[])
    def following(self, request, pk):
        obj = self.queryset.get(id=int(pk))
        
        from rest_framework.reverse import reverse
        def reverse_url(result):
            return reverse('%s-detail'%result.target._meta.object_name.lower(), args=[result.target.id])
        
        results = Follow.objects.filter(user=obj)
        results = [{'url': reverse_url(result), 'type': result.target._meta.object_name, '__str__': str(result.target) } for result in results]

        return Response(results)
        

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
    
    def can_change_follow(self, user, obj):
        # Don't allow project owners to unfollow the project
        return user.id != obj.author.id
    
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

    
