from django.contrib import admin
from django.utils.translation import ugettext as _

from reversion import VersionAdmin

from django_project.models import Component
from django_project.models import Membership
from django_project.models import Milestone
from django_project.models import Priority
from django_project.models import Project
from django_project.models import Task
from django_project.models import TaskType

from django_project.models import Status
from django_project.models import Transition

from django_project.models import Comment


class StatusAdmin(admin.ModelAdmin):
    list_display = ( 'id', 'name', 'order', 'is_resolved', 'project')
    list_display_links = ('id',)
    list_editable = ( 'name', 'order', 'is_resolved', )
    list_filter = ('project',)
    #readonly_fields = ['project']
    

class TaskAdmin(VersionAdmin):
    list_display = ( 'project', 'component', 'id', 'summary',
        'created_at', 'author', 'status', 'priority', 'type', 'nr_of_versions')
    list_display_links = ('summary',)
    list_filter = ('project',)
    date_hierarchy = 'created_at'
    save_on_top = True
    search_fields = ['id', 'summary', 'description']

    fieldsets = (
        (_("Task detail"), {
            'fields': (
                'summary',
                ('project', 'component'),
                'description',
                'status',
                'priority',
                'type',
                'owner',
                'milestone',
                'deadline',
            )
        }),
        (_("Author & editor"), {
            #'classes': ['collapsed collapse-toggle'],
            'fields': (
                ('author', 'author_ip'),
                ('editor', 'editor_ip'),
            ),
        }),
    )

    # This option would be used from Django 1.2
    #readonly_fields = ('author_ip', 'editor_ip')


class OrderedDictModelAdmin(admin.ModelAdmin):
    list_display = ( 'id', 'name', 'order', 'description' )
    list_display_links = ( 'id', 'name' )
    list_editable = ( 'order', )

class MilestoneInline(admin.TabularInline):
    model = Milestone
    extra = 1

class TaskTypeInline(admin.TabularInline):
    model = TaskType
    extra = 1

class ComponentInline(admin.TabularInline):
    model = Component
    extra = 1

class StatusInline(admin.TabularInline):
    model = Status
    extra = 1

class PriorityInline(admin.TabularInline):
    model = Priority
    extra = 1


class ComponentAdmin(admin.ModelAdmin):
    list_display = 'project', 'name', 'description'
    list_display_links = 'name',
    list_filter = 'project',
    search_fields = ['project', 'name']


class TaskTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'project', 'name', 'order']
    list_display_links = ['name']
    list_filter = ['project']
    search_field = ['name', 'project']


admin.site.register(Transition)
admin.site.register(Status, StatusAdmin)

admin.site.register(Priority, OrderedDictModelAdmin)
admin.site.register(TaskType, TaskTypeAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Project)
admin.site.register(Membership)
admin.site.register(Component)
admin.site.register(Milestone)

admin.site.register(Comment)



