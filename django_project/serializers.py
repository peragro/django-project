import os
import urllib

from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework.relations import HyperlinkedRelatedField

from notifications.models import Notification
from follow.models import Follow

from django_project.models import Project, Task, Milestone, Component, Comment
from django_project import models


class FollowSerializerMixin(object):
    def to_native(self, obj):
        ret = super(FollowSerializerMixin, self).to_native(obj)
        if obj and 'request' in self.context:
            ret['is_following'] = Follow.objects.is_following(self.context['request'].user, obj)
        return ret


class FollowSerializer(serializers.Serializer):
    def to_native(self, obj):
        def reverse_url(result):
            return reverse('%s-detail'%result.target._meta.object_name.lower(), args=[result.target.id])
            
        ret = {'url': reverse_url(obj), 'type': obj.target._meta.object_name, '__str__': str(obj.target) }
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


class UserNameSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.CharField(source='username', read_only=True)
    class Meta:
        model = User
        fields = ('id', 'url', 'name')        
        

class MilestoneSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)
    class Meta:
        model = Milestone


class ProjectMemberSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'url', 'username')


class ProjectSerializer(FollowSerializerMixin, serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)
    members = ProjectMemberSerializer(many=True)
    author_descr = serializers.CharField(source='author', read_only=True)
    class Meta:
        model = Project


class ComponentSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)
    class Meta:
        model = Component
        read_only_fields = ('project', )


class TaskTypeSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = models.TaskType


class PrioritySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Priority


class StatusSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Status
        

class TaskSerializer(FollowSerializerMixin, serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)
    status_descr = serializers.CharField(source='status', read_only=True)
    priority_descr = serializers.CharField(source='priority', read_only=True)
    type_descr = serializers.CharField(source='type', read_only=True)
    component_descr = serializers.CharField(source='component', read_only=True)
    
    author_descr = serializers.CharField(source='author', read_only=True)
    owner_descr = serializers.CharField(source='owner', read_only=True)
    
    class Meta:
        model = Task
        read_only_fields = ('author', 'project') 
        
    def save_object(self, task, *args, **kwargs):
        task.save_revision(self.context['request'].user, task.description, *args, **kwargs) #TODO: add interesting commit message!


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
        

class GenericForeignKeyMixin(object):
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


class NotificationSerializer(GenericForeignKeyMixin, serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
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





class VersionSerializer(serializers.Serializer):
    def to_native(self, version):
        ver = {}
        ver['revision'] = {}
        ver['revision']['comment'] = version.revision.comment
        ver['revision']['editor'] = version.revision.user.username
        ver['revision']['revision_id'] = version.revision_id
        ver['revision']['date_created'] = version.revision.date_created
        ver['object'] = version.field_dict
        return ver
        
        
class CommentSerializer(GenericForeignKeyMixin, serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)
    #content_object_descr = serializers.CharField(source='content_object', read_only=True)
    #content_object = SerializerMethodFieldArgs('get_related_object_url', 'content_object')  
    
    author_descr = serializers.CharField(source='author', read_only=True)
    author = SerializerMethodFieldArgs('get_related_object_url', 'author')
    
    class Meta:
        model = Comment
        #fields = ('comment',)
        exclude = ('content_type', 'object_pk', )
        write_only_fields = ('comment',) 
        
    def get_parent_object(self, instance=None):
        if instance:
            return instance.content_object
        else:
            from django.core.urlresolvers import resolve
            #TODO: there must be a better way to get the parent viewset????
            path = '/'.join(self.context['request'].path.split('/')[:-2])+'/'
            parent_viewset = resolve(path)
            object = parent_viewset.func.cls.queryset.get(**parent_viewset.kwargs)
            return object
        
    def restore_object(self, attrs, instance=None):
        #assert instance is None, 'Cannot update comment with CommentSerializer'      
        
        object = self.get_parent_object(instance)   
        values = {'comment': attrs['comment'], 'content_object':object, 'author':self.context['request'].user}                       
        if instance:
            for (key, value) in values.items():
                setattr(instance, key, value)
            return instance
        else:
            comment = Comment(**values)
            return comment
        
