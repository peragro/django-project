import os
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import resolve

from django.contrib.comments.models import Comment

from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action, link
from rest_framework import status
from rest_framework import filters

from rest_framework.permissions import IsAuthenticated

from notifications.models import Notification

from follow.models import Follow
import follow

from django_project.serializers import UserSerializer, GroupSerializer, FollowSerializer, VersionSerializer, CommentSerializer
from django_project.serializers import ProjectSerializer, MilestoneSerializer, TaskSerializer, NotificationSerializer, ComponentSerializer

from django_project.models import Project, Task, Milestone, Component

from django_project import signals
from django_project import filters as dp_filters


class FollowingModelViewSet(viewsets.ModelViewSet):
    def metadata(self, request):
        print('-'*80)
        #for field in dir(request):
        #    print('field: ', field, '-->', getattr(request, field))
        print('-'*80)
        path = request._request.path
        print(path)
        ret = super(FollowingModelViewSet, self).metadata(request)
        if 'pk' in self.kwargs:
            methods = []
            
            methods.append({'url': path+'follow/', 'methods': ['POST', 'DELETE']})
            methods.append({'url': path+'followers/', 'methods': ['GET']})
            methods.append({'url': path+'activity/', 'methods': ['GET']})
            
            if 'methods' in ret:
                ret['methods'] = []
            ret['methods'].extend(methods)
        return ret
        
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
        
        serializer = paginate_data(self, users, UserSerializer)

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
        
        serializer = paginate_data(self, notifications, NotificationSerializer)

        return Response(serializer.data)


class NestedViewSetMixin(object):
    def get_queryset(self):
        """
        NestedSimpleRouter support for Viewset.
        Filter the nested objects using the parent through the 'lookup' field.
        Its format is either:
        - <ViewSet1>__<fielda>11<ViewSet2>__<fieldb>
        - <field>
        For Example:
        class Project:
            pass
        class Task:
            belongs_to_project = ForeignKey(Project)
        class Component:
            project = ForeignKey(Project)
        projects_router = routers.NestedSimpleRouter(router, r'projects', lookup='belongs_to_project')
        projects_router.register(r'tasks', views.TaskViewSet)
        or
        projects_router = routers.NestedSimpleRouter(router, r'projects', lookup='TaskViewSet__belongs_to_project11ComponentsViewSet__project')
        projects_router.register(r'tasks', views.TaskViewSet)
        projects_router.register(r'components', views.ComponentsViewSet)
        """
        qs = super(viewsets.ModelViewSet, self).get_queryset()
        print('ComponentViewSet', self.__class__.__name__)
        print('ComponentViewSet', self.kwargs)

        path = self.request._request.path
        print(path)
        print(dir(resolve(path).func))
        blah = resolve(path).func.cls
        for field in dir(blah):
            try:
                print(field+' -->'+str(getattr(blah, field)))
            except:
                pass

        def handle_field(filter, field_name, value):
            field = getattr(qs.model, field_name)
            if field.__class__.__name__ =="GenericForeignKey":
                #TODO: there must be a better way to get the parent viewset????
                path = '/'.join(self.request._request.path.split('/')[:-3])+'/'
                parent_viewset = resolve(path).func.cls
                ct = ContentType.objects.get_for_model(parent_viewset.queryset.model)
                filter[field.fk_field] = int(value)
                filter[field.ct_field] = ct
            else:
                filter[field] = int(value)
            
        filter = {}
        for key, value in self.kwargs.items():
            if key.endswith('_pk'):
                names = key[:-len('_pk')].split('11')
                names = dict([name.split('__')  if name.find('__')>-1 else (None, name) for name in names])
                print(names)
                name = self.__class__.__name__ # <ViewSet>
                if name in names:
                    field = names[name]
                    handle_field(filter, field, value)
                elif None in names:
                    field = names[None]
                    handle_field(filter, field, value)
                    
        if len(filter)==0:
            raise Exception('NestedViewSetMixin: could not figure the filter to use for the nested route %s %s. Did you give a lookup param to NestedSimpleRouter'%(self, self.kwargs))
        print('ComponentViewSet', filter)
        qs =  qs.filter(**filter)
        return qs


class FilteredModelViewSetMixin(object):
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter,)
    
    def metadata(self, request):
        ret = super(FilteredModelViewSetMixin, self).metadata(request)
        if 'pk' not in self.kwargs:
            f = self.filter_class(request.GET, queryset=self.get_queryset())
            if hasattr(self, 'search_fields'):
                ret['search'] = {'search_by_field': 'search', 'searches': self.search_fields}
            if hasattr(self, 'filter_class') and hasattr(self.filter_class.Meta, 'order_by'):
                ret['ordering'] = {'order_by_field': f.order_by_field, 'choices': f.ordering_field.choices}
            if len(f.filters):
                ret['filtering'] = {}
                for name, field in f.filters.items():
                    if 'queryset' in field.extra:
                        ret['filtering'][name] = {'values': [(opt.id, str(opt)) for opt in field.extra['queryset']]}
                    else:
                        ret['filtering'][name] = {'searches': field.lookup_type}

        return ret
        
#-----------------------------------------------------------------------        

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
    def following(self, request, pk):
        obj = self.queryset.get(id=int(pk))
        
        results = Follow.objects.filter(user=obj)
        serializer = paginate_data(self, results, FollowSerializer)
        
        return Response(serializer.data)


class CurrentUserDetail(APIView):
    """
    Retrieve the current User
    """
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, format=None):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class GroupViewSet(FollowingModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class ProjectViewSet(NestedViewSetMixin, FilteredModelViewSetMixin, FollowingModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    notifications_field = 'target'
    filter_class = dp_filters.ProjectFilter
    search_fields = ('author__username', 'name')
    
    def can_change_follow(self, user, obj):
        # Don't allow project owners to unfollow the project
        return user.id != obj.author.id


class ComponentViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows Components to be viewed or edited.
    """
    queryset = Component.objects.all()
    serializer_class = ComponentSerializer


class TaskViewSet(NestedViewSetMixin, FilteredModelViewSetMixin, FollowingModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    notifications_field = 'action_object'
    filter_class = dp_filters.TaskFilter
    search_fields = ('summary', 'description')
    
    def metadata(self, request):
        ret = super(FollowingModelViewSet, self).metadata(request)
        if 'pk' in self.kwargs:
            methods = []
            methods.append({'url': path+'revisions/', 'methods': ['GET']})
            
            if 'methods' in ret:
                ret['methods'] = []
            ret['methods'].extend(methods)
        return ret

    @link(permission_classes=[])
    def revisions(self, request, pk, **kwargs):
        task = self.queryset.get(id=int(pk))
        versions = task.versions()
        print(versions)
        for field in dir(versions[0].revision):
            try:
                print(field+' -->'+str(getattr(versions[0].revision, field)))
            except:
                pass

        serializer = paginate_data(self, versions, VersionSerializer)

        return Response(serializer.data)


class CommentModelViewSet(NestedViewSetMixin, FilteredModelViewSetMixin, viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    filter_class = dp_filters.CommentFilter
    search_fields = ('user__username', 'comment')
    

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
        
