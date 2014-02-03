import django_filters
from django.contrib.comments.models import Comment

from django_project import models

class TaskFilter(django_filters.FilterSet):
    #http://stackoverflow.com/questions/10873249/django-filter-lookup-type-documentation
    owner = django_filters.CharFilter(name="owner__username", lookup_type="icontains")
    author = django_filters.CharFilter(name="author__username", lookup_type="icontains")
    class Meta:
        model = models.Task
        fields = ['owner', 'author', 'status', 'component', 'milestone']    
        order_by = (
                        ('status__order', 'Status'),
                        ('priority__order', 'Priority'),
                        ('-status__order', 'Status'),
                        ('-priority__order', 'Priority'),
                        ('deadline', 'Dead line'),
                        ('-deadline', 'Dead line'),
                    )
            
class ProjectFilter(django_filters.FilterSet):

    class Meta:
        model = models.Project
        fields = ['name', 'author', 'created_at', 'modified_at']    
        order_by = (
                        ('name', 'Name'),
                        ('-name', 'Name'),
                        ('created_at', 'Created at'),
                        ('-created_at', 'Created at'),
                        ('modified_at', 'Modified at'),
                        ('-modified_at', 'Modified at'),
                    )

class CommentFilter(django_filters.FilterSet):
    class Meta:
        model = Comment
