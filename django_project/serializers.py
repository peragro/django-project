import os
import urllib

from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework.relations import HyperlinkedRelatedField

from notifications.models import Notification
from follow.models import Follow

from django_project.models import Project, Task, Milestone, Component


class FollowSerializerMixin(object):
    def to_native(self, obj):
        ret = super(FollowSerializerMixin, self).to_native(obj)
        if obj and 'request' in self.context:
            ret['is_following'] = Follow.objects.is_following(self.context['request'].user, obj)
        return ret


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'url', 'name')


class UserSerializer(FollowSerializerMixin, serializers.HyperlinkedModelSerializer):
    groups = GroupSerializer(many=True)
    class Meta:
        model = User
        fields = ('id', 'url', 'username', 'email', 'groups')
        
        

class MilestoneSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Milestone
        fields = ('id', 'name',)


class ProjectSerializer(FollowSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Project
        fields = ('id', 'url', 'name',)


class ComponentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Component
        fields = ('id', 'url', 'name',)
    

class TaskSerializer(FollowSerializerMixin, serializers.HyperlinkedModelSerializer):
    status = serializers.CharField()
    priority = serializers.CharField()
    type = serializers.CharField()
    component = ComponentSerializer()
    
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
    id = serializers.IntegerField()
    level = serializers.CharField()
    
    recipient_descr = serializers.CharField(source='recipient', read_only=True)
    recipient = SerializerMethodFieldArgs('get_related_object_url', 'recipient')
    
    actor_descr = serializers.CharField(source='actor', read_only=True)
    actor = SerializerMethodFieldArgs('get_related_object_url', 'actor')
    
    verb = serializers.CharField()
    description = serializers.CharField()
    
    target_descr = serializers.CharField(source='target', read_only=True)
    target = SerializerMethodFieldArgs('get_related_object_url', 'target')
    
    action_object_descr = serializers.CharField(source='action_object', read_only=True)
    action_object = SerializerMethodFieldArgs('get_related_object_url', 'action_object')
    
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

