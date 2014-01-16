import os
import urllib

from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework.reverse import reverse

from notifications.models import Notification

from django_project.models import Project, Task

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')
        
class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Project
        fields = ('name',)


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    status = serializers.CharField()
    priority = serializers.CharField()
    type = serializers.CharField()
    component = serializers.CharField()
    
    class Meta:
        model = Task
        #fields = ('summary',)
        
class SerializerMethodFieldArgs(serializers.Field):
    """
    A field that gets its value by calling a method on the serializer it's attached to.
    """
    def __init__(self, method_name, *args):
        self.method_name = method_name
        self.args = args
        super(SerializerMethodFieldArgs, self).__init__()

    def field_to_native(self, obj, field_name):
        value = getattr(self.parent, self.method_name)(obj, *self.args)
        return self.to_native(value)


class NotificationSerializer(serializers.Serializer):
    level = serializers.CharField()
    
    recipient = serializers.CharField()
    recipient_url = SerializerMethodFieldArgs('get_related_object_url', 'recipient')
    
    actor = serializers.CharField()
    actor_url = SerializerMethodFieldArgs('get_related_object_url', 'actor')
    
    verb = serializers.CharField()
    description = serializers.CharField()
    
    target = serializers.CharField()
    target_url = SerializerMethodFieldArgs('get_related_object_url', 'target')
    
    action_object = serializers.CharField()
    action_object_url = SerializerMethodFieldArgs('get_related_object_url', 'action_object')
    
    timesince = serializers.CharField()
    
    __str__ = serializers.CharField()


    def get_related_object_url(self, obj, field):
        try:
            obj = getattr(obj, field)
            default_view_name = '%(model_name)s-detail'
            
            format_kwargs = {
                'app_label': obj._meta.app_label,
                'model_name': obj._meta.object_name.lower()
            }
            view_name = default_view_name % format_kwargs
            print('get_related_object_url::view_name', view_name)
            s = serializers.HyperlinkedIdentityField(source=obj, view_name=view_name)
            s.initialize(self, None)
            return s.field_to_native(obj, None)
        except Exception as e:
            print(e)
            return ''

