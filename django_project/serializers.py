import os
import urllib

from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework.relations import HyperlinkedRelatedField
from rest_framework.relations import RelatedField

from notifications.models import Notification
from follow.models import Follow

from django_project.models import Project, Task, Milestone, Component, Comment, ObjectTask
from django_project import models


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


class HyperlinkedRelatedMethod(RelatedField):
    """
    A field that replaces usage of:
    class A(GenericForeignKeyMixin):
      field = SerializerMethodFieldArgs('get_related_object_url', 'field')
    """
    def __init__(self):
        super(HyperlinkedRelatedMethod, self).__init__()

    def field_to_native(self, obj, field_name):
        value = GenericForeignKeyMixin.get_related_object_url(self.parent, obj, field_name)
        return self.to_native(value)


class GenericForeignKeyMixin(object):
    def get_related_object_url(self, obj, field):
        try:
            obj = getattr(obj, field)
            if callable(obj):
              obj = obj()
            default_view_name = '%(model_name)s-detail'

            format_kwargs = {
                'app_label': obj._meta.app_label,
                'model_name': obj._meta.object_name.lower()
            }
            view_name = default_view_name % format_kwargs
            print('*get_related_object_url::view_name', view_name)
            s = serializers.HyperlinkedIdentityField(source=obj, view_name=view_name)
            s.initialize(self, None)
            return s.field_to_native(obj, None)
        except Exception as e:
            print('WARN', e)
            return None


class ExtendedHyperlinkedModelSerializer(serializers.HyperlinkedModelSerializer):
    def to_native(self, obj):
        res = super(ExtendedHyperlinkedModelSerializer, self).to_native(obj)
        if obj:
            res['id'] = obj.serializable_value('pk')
            for field_name, field in self.fields.items():
                if isinstance(field , HyperlinkedRelatedMethod):
                  serializable_value = obj.serializable_value(field_name)()
                  res[field_name] = {'url': res[field_name]}
                  res[field_name]["id"] = serializable_value.pk if serializable_value else None
                  res[field_name]["descr"] = str(serializable_value) if serializable_value else None
                elif isinstance(field , RelatedField):
                    serializable_value = obj.serializable_value(field_name)
                    res[field_name] = {'url': res[field_name]}
                    if isinstance(serializable_value, int):
                        res[field_name]["id"] = obj.serializable_value(field_name)
                        res[field_name]["descr"] = str(getattr(obj, field_name))
                    elif serializable_value == None:
                        res[field_name]["id"] = None
                        res[field_name]["descr"] = None
                else:
                  print field_name, field.__class__
        return res


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


class GroupSerializer(ExtendedHyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'url', 'name')


class UserSerializer(FollowSerializerMixin, ExtendedHyperlinkedModelSerializer):
    groups = GroupSerializer(many=True)
    class Meta:
        model = User
        fields = ('id', 'url', 'username', 'email', 'groups')


class UserNameSerializer(ExtendedHyperlinkedModelSerializer):
    name = serializers.CharField(source='username', read_only=True)
    class Meta:
        model = User
        fields = ('id', 'url', 'name')


class MilestoneSerializer(ExtendedHyperlinkedModelSerializer):
    class Meta:
        model = Milestone


class ProjectMemberSerializer(ExtendedHyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'url', 'username')


class ProjectSerializer(FollowSerializerMixin, ExtendedHyperlinkedModelSerializer):
    members = ProjectMemberSerializer(many=True)
    author = serializers.PrimaryKeyRelatedField(required=False, read_only=False)
    class Meta:
        model = Project
        exclude = ('members', )

    def validate_author(self, attrs, source):
        if attrs[source] is None:
            attrs[source] = self.context['request'].user

        return attrs


class ComponentSerializer(ExtendedHyperlinkedModelSerializer):
    class Meta:
        model = Component
        read_only_fields = ('project', )


class TaskTypeSerializer(ExtendedHyperlinkedModelSerializer):
    class Meta:
        model = models.TaskType


class PrioritySerializer(ExtendedHyperlinkedModelSerializer):
    class Meta:
        model = models.Priority


class StatusSerializer(ExtendedHyperlinkedModelSerializer):
    class Meta:
        model = models.Status


class ObjectTaskSerializer(GenericForeignKeyMixin, serializers.Serializer):
    content_object = SerializerMethodFieldArgs('get_related_object_url', 'content_object')
    content_object_descr = serializers.CharField(source='content_object', read_only=True)


class TaskSerializer(FollowSerializerMixin, ExtendedHyperlinkedModelSerializer):
    objecttask_tasks = ObjectTaskSerializer(many=True, read_only=True)
    class Meta:
        model = Task
        read_only_fields = ('author', 'project')

    def save_object(self, task, *args, **kwargs):
        task.save_revision(self.context['request'].user, task.description, *args, **kwargs) #TODO: add interesting commit message!


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



class RelatedSerializer(serializers.Serializer):
    def to_native(self, version):
        ver = {}
        ver['id'] = version.id
        #ver['dir'] = dir(version)
        ver['object'] = version.field_dict
        #ver['object_version'] = version.object_version
        return ver


class VersionSerializer(serializers.Serializer):
    def to_native(self, version):
        ver = {}
        ver['id'] = version.id
        ver['revision'] = {}
        ver['revision']['comment'] = version.revision.comment
        if version.revision.user:
            ver['revision']['editor'] = version.revision.user.username
        else:
            ver['revision']['editor'] = 'Anonymous'
        ver['revision']['revision_id'] = version.revision_id
        ver['revision']['related'] = RelatedSerializer(version.revision.version_set.exclude(pk=version.pk).all(), many=True).data
        ver['revision']['date_created'] = version.revision.date_created
        ver['object'] = version.field_dict
        ver['m2m_data'] = version.object_version.m2m_data
        return ver


class CommentSerializer(GenericForeignKeyMixin, ExtendedHyperlinkedModelSerializer):
    content_object = SerializerMethodFieldArgs('get_related_object_url', 'content_object')
    content_object_descr = serializers.CharField(source='content_object', read_only=True)

    class Meta:
        model = Comment
        exclude = ('content_type', 'object_pk', )

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
