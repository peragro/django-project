import django_filters

from django_project import models


from datetime import timedelta
from django.utils.timezone import now
from django_filters.filters import _truncate
from django_filters.filters import Filter
class ExtendedDateRangeFilter(Filter):
    def __init__(self, *args, **kwargs):
        super(ExtendedDateRangeFilter, self).__init__(*args, **kwargs)

    def filter(self, qs, value):
        try:
            value = int(value)
        except (ValueError, TypeError):
            value = 0
        if value >= 0:
            return qs.filter(**{
                '%s__gte' % self.name: _truncate(now() + timedelta(days=1)),
                '%s__lt' % self.name: _truncate(now() + timedelta(days=value)),
                })
        else:
            return qs.filter(**{
                '%s__gte' % self.name: _truncate(now() - timedelta(days=-value)),
                '%s__lt' % self.name: _truncate(now() + timedelta(days=1)),
                })

        
class TaskFilter(django_filters.FilterSet):
    #http://stackoverflow.com/questions/10873249/django-filter-lookup-type-documentation
    owner = django_filters.CharFilter(name="owner__username", lookup_type="icontains")
    author = django_filters.CharFilter(name="author__username", lookup_type="icontains")
    deadline = ExtendedDateRangeFilter()
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
        model = models.Comment
        order_by = (
                        ('submit_date', 'Date'),
                        ('-submit_date', 'Date'),
                    )

class MilestoneFilter(django_filters.FilterSet):
    deadline = ExtendedDateRangeFilter()
    class Meta:
        model = models.Milestone
