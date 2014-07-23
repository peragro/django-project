import os
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import resolve

from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework import filters

from rest_framework.permissions import IsAuthenticated

from notifications.models import Notification

from follow.models import Follow
import follow

from rest_framework_extensions.decorators import action, link
from rest_framework_extensions.mixins import NestedViewSetMixin

from django_project import serializers
from django_project import models

from django_project import signals
from django_project import filters as dp_filters

class MetaDataModelViewSet(viewsets.ModelViewSet):
    """
    Collects metadata of each subclass(methods aren't overridden)
    using 'metadata_<entry>()' methods.
    """
    def metadata(self, request):
        ret = super(MetaDataModelViewSet, self).metadata(request)
        
        mros = type(self).mro() # Get the Inheritance tree
        for mro in mros:
            for method in mro.__dict__: # Only iterate non-inherted class methods
                if method.startswith('metadata_'):
                    name = method[len('metadata_'):]
                    val = getattr(mro, method)(self, request)
                    if val:
                        is_dict = type(val) is dict
                        if name not in ret:
                            ret[name] = {} if is_dict else []
                        if is_dict:
                            ret[name].update(val)
                        else:
                            ret[name].extend(val)

        return ret


class FollowingModelViewSet(MetaDataModelViewSet):
    def metadata_methods(self, request):
        print('FollowingModelViewSet::metadata_methods', self.kwargs) 
        if has_instance_key(self.kwargs):
            path = request._request.path
            methods = []
            
            methods.append({'url': path+'follow/', 'methods': ['POST', 'DELETE']})
            methods.append({'url': path+'followers/', 'methods': ['GET']})
            methods.append({'url': path+'activity/', 'methods': ['GET']})

            return methods
    
    def metadata_filtering(self, request):   
        return {'is_following': {'searches': 'exact'}}
        
    def get_queryset(self):
        qs = super(FollowingModelViewSet, self).get_queryset()
        if self.request.QUERY_PARAMS.get('is_following', '').lower() == 'true' and self.request.user.is_authenticated():
            qs = qs.filter(**{'follow_%s__user'%qs.model._meta.model_name: self.request.user})
        return qs
                
    @action(methods=['POST', 'DELETE'], permission_classes=[IsAuthenticated])
    def follow(self, request, pk, **kwargs):  
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
    def followers(self, request, pk, **kwargs):    
        obj = self.queryset.get(id=int(pk))
        
        users = User.objects.filter(id__in=Follow.objects.get_follows(obj).values_list('user'))
        
        serializer = paginate_data(self, users, serializers.UserSerializer)

        return Response(serializer.data)
        
    @link()
    def activity(self, request, pk, **kwargs):
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
        
        serializer = paginate_data(self, notifications, serializers.NotificationSerializer)

        return Response(serializer.data)


def nested_viewset_with_genericfk(parent_viewset, viewset):
    class Wrapper(viewset):
        def get_queryset(self):
            return super(Wrapper, self).get_queryset().filter(
                content_type=ContentType.objects.get_for_model(parent_viewset.queryset.model)
            )
    return Wrapper


class FilteredModelViewSetMixin(object):
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter,)
    
    def metadata(self, request):
        from django_filters import DateRangeFilter
        ret = super(FilteredModelViewSetMixin, self).metadata(request)
        if 'pk' not in self.kwargs:
            f = self.filter_class(request.GET, queryset=self.get_queryset())
            if hasattr(self, 'search_fields'):
                ret['search'] = {'search_by_field': 'search', 'searches': self.search_fields}
            if hasattr(self, 'filter_class') and hasattr(self.filter_class.Meta, 'order_by'):
                ret['ordering'] = {'order_by_field': f.order_by_field, 'choices': f.ordering_field.choices}
            if len(f.filters):
                ret['filtering'] = ret.get('filtering', {})
                for name, field in f.filters.items():
                    if 'queryset' in field.extra:
                        ret['filtering'][name] = {'values': [(opt.id, str(opt)) for opt in field.extra['queryset']]}
                    elif isinstance(field, DateRangeFilter):
                        print field.options
                        ret['filtering'][name] = {'values': [(id, tup[0]) for id, tup in field.options.items()]}
                    else:
                        ret['filtering'][name] = {'searches': field.lookup_type}

        return ret


class StatisticsViewSetMixin(object): 
    @link(is_for_list=True)
    def statistics(self, request, **kwargs):
        from datetime import datetime
        qs = self.get_queryset()
        ret = {}
        ret['Total'] = qs.count()
        ret['Todo'] = qs.exclude(deadline__lt=datetime.now()).exclude(owner=None).exclude(status__is_resolved=True).count()
        ret['Past Due'] = qs.filter(deadline__lt=datetime.now()).count()
        ret['Unassigned'] = qs.filter(owner=None).count()
        ret['Complete'] = qs.filter(status__is_resolved=True).count()
        return Response(ret)       
#-----------------------------------------------------------------------        

class UserViewSet(NestedViewSetMixin, FollowingModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    notifications_field = 'recipient'
    
    def can_change_follow(self, user, obj):
        # Don't allow users to follow themselfs
        return user.id != obj.id
        
    @link(permission_classes=[])
    def following(self, request, pk):
        obj = self.queryset.get(id=int(pk))
        
        results = Follow.objects.filter(user=obj)
        serializer = paginate_data(self, results, serializers.FollowSerializer)
        
        return Response(serializer.data)


class CurrentUserDetail(APIView):
    """
    Retrieve the current User
    """
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, format=None):
        serializer = serializers.UserSerializer(request.user)
        return Response(serializer.data)


class GroupViewSet(FollowingModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = serializers.GroupSerializer


class ProjectViewSet(NestedViewSetMixin, FilteredModelViewSetMixin, FollowingModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer
    notifications_field = 'target'
    filter_class = dp_filters.ProjectFilter
    search_fields = ('author__username', 'name')
    
    def can_change_follow(self, user, obj):
        # Don't allow project owners to unfollow the project
        return user.id != obj.author.id


class MilestoneModelViewSet(NestedViewSetMixin, FilteredModelViewSetMixin, viewsets.ModelViewSet):
    queryset = models.Milestone.objects.all()
    serializer_class = serializers.MilestoneSerializer
    filter_class = dp_filters.MilestoneFilter


class ComponentViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows Components to be viewed or edited.
    """
    queryset = models.Component.objects.all()
    serializer_class = serializers.ComponentSerializer


class TaskTypeViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows TaskTypes to be viewed or edited.
    """
    queryset = models.TaskType.objects.all()
    serializer_class = serializers.TaskTypeSerializer


class PriorityViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows Priorities to be viewed or edited.
    """
    queryset = models.Priority.objects.all()
    serializer_class = serializers.PrioritySerializer


class StatusViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows Statuses to be viewed or edited.
    """
    queryset = models.Status.objects.all()
    serializer_class = serializers.StatusSerializer    


class TaskViewSet(StatisticsViewSetMixin, NestedViewSetMixin, FilteredModelViewSetMixin, FollowingModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = models.Task.objects.all()
    serializer_class = serializers.TaskSerializer
    notifications_field = 'action_object'
    filter_class = dp_filters.TaskFilter
    search_fields = ('summary', 'description')


    def pre_save(self, obj):
        obj.author = self.request.user
        #TODO: validate this is a nested view when saving
        if not hasattr(obj, 'project') or not obj.project:
            project_pk = self.kwargs['parent_lookup_project']
            obj.project = models.Project.objects.get(id=int(project_pk))
        
    def metadata_methods(self, request):
        print('TaskViewSet::metadata_methods')
        if has_instance_key(self.kwargs):
            path = request._request.path
            methods = []
            methods.append({'url': path+'revisions/', 'methods': ['GET']})
            return methods
    
    def metadata_options(self, request):    
        print('TaskViewSet::metadata_options')
        project_pk = None
        if has_primary_key(self.kwargs):
            if 'project_pk' in self.kwargs:
                project_pk = self.kwargs['project_pk']
        elif has_instance_key(self.kwargs):
            task = self.queryset.get(id=int(self.kwargs['pk']))
            project_pk = task.project.id
            
            if project_pk:
                data = {}   
                for model, field in [('Priority', 'priority'), ('TaskType', 'type'), ('Component', 'component'), ('Milestone', 'milestone')]:
                    qs = getattr(models, model).objects.filter(project_id=int(project_pk))
                    data[field] = getattr(serializers, model+'Serializer')(qs, many=True, context={'request': request}).data
                for model, field in [('User', 'owner')]:
                    qs = getattr(models, model).objects.filter(membership__project_id=int(project_pk))
                    data[field] = getattr(serializers, model+'NameSerializer')(qs, many=True, context={'request': request}).data
                    
                for model, field in [('Status', 'status')]:
                    if 'pk' in self.kwargs: 
                        #We're holding a task for editting. So only return allowed transitions.
                        task = self.queryset.get(id=int(self.kwargs['pk']))
                        qs = getattr(models, model).objects.filter(transition__source=task.status)
                    else:
                        #We're going to create a task, so only return intial statuses.
                        qs = getattr(models, model).objects.filter(project_id=int(project_pk), is_initial=True)
                    data[field] = getattr(serializers, model+'Serializer')(qs, many=True, context={'request': request}).data
                return data
    
    @link(permission_classes=[])
    def revisions(self, request, pk, **kwargs):
        task = self.queryset.get(id=int(pk))
        versions = task.versions()

        serializer = paginate_data(self, versions, serializers.VersionSerializer)

        return Response(serializer.data)
    
    @link(permission_classes=[])
    def objects(self, request, pk, **kwargs):
        task = self.queryset.get(id=int(pk))
        objects = task.objecttask_tasks.all()

        serializer = paginate_data(self, objects, serializers.ObjectTaskSerializer)

        return Response(serializer.data)    

class CommentModelViewSet(NestedViewSetMixin, FilteredModelViewSetMixin, viewsets.ModelViewSet):
    queryset = models.Comment.objects.all()
    serializer_class = serializers.CommentSerializer
    filter_class = dp_filters.CommentFilter
    search_fields = ('user__username', 'comment')


class NotificationModelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = serializers.NotificationSerializer

    

def has_primary_key(kwargs):
    return (True in map(lambda x: x.endswith('_pk'), kwargs.keys()))

def has_instance_key(kwargs):
    return 'pk' in kwargs

def paginate_data(self, data, serializer_class=None):
    from rest_framework.pagination import PaginationSerializer
    page = self.paginate_queryset(data)
    if serializer_class:
        class SerializerClass(PaginationSerializer):
                class Meta:
                    object_serializer_class = serializer_class

        pagination_serializer_class = SerializerClass
        context = self.get_serializer_context()
        return pagination_serializer_class(instance=page, context=context)
    else:
        
        return PaginationSerializer(instance=page)
        
