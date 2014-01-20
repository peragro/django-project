import django_filters
from django_project import models

class TaskFilter(django_filters.FilterSet):

    owner = django_filters.CharFilter(name="owner__username")
    status = django_filters.CharFilter(name="status__name")
    class Meta:
        model = models.Task
        fields = ['owner', 'status']    
        order_by = (
                        ('status__order', 'Status'),
                        ('priority__order', 'Priority'),
                        ('-status__order', 'Status'),
                        ('-priority__order', 'Priority'),
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
