import datetime

from django.db import models
from django.contrib.auth.models import User, Group, AnonymousUser, Permission

from django.utils.translation import ugettext_lazy as __
from django.utils.translation import ugettext as _

from autoslug import AutoSlugField


from django_project.mixins import TaskMixin


class Project(models.Model):
    """
    """
    name = models.CharField(_('name'), max_length=64)
    slug = AutoSlugField(max_length=128, populate_from='name', unique_with='author')
    
    author = models.ForeignKey(User, name=_('author'), related_name='created_projects')
    
    members = models.ManyToManyField(User, verbose_name=_('members'), through="Membership")
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    modified_at = models.DateTimeField(_('modified at'), auto_now=True)
    

    class Meta:
        #verbose_name = _('project')
        #verbose_name_plural = _('projects')
        #ordering = ['name']
        #get_latest_by = 'created_at'
        #unique_together = ['author', 'name']
        permissions = (
            ('view_project', 'Can view project'),
            ('admin_project', 'Can administer project'),
            ('can_read_repository', 'Can read repository'),
            ('can_write_to_repository', 'Can write to repository'),
            ('can_add_task', 'Can add task'),
            ('can_change_task', 'Can change task'),
            ('can_delete_task', 'Can delete task'),
            ('can_view_tasks', 'Can view tasks'),
            ('can_add_member', 'Can add member'),
            ('can_change_member', 'Can change member'),
            ('can_delete_member', 'Can delete member'),
        )
        
    def __unicode__(self):
        return self.name

class Component(models.Model):
    """
    """
    project = models.ForeignKey(Project)
    name = models.CharField(max_length=64)
    slug = AutoSlugField(max_length=64, populate_from='name', always_update=True, unique_with='project')
    description = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = _('component')
        verbose_name_plural = _('components')
        ordering = ('name',)
        unique_together = ('project', 'name')

    def __unicode__(self):
        return self.name


class Membership(models.Model):
    """
    """
    member = models.ForeignKey(User, verbose_name=_('member'))
    project = models.ForeignKey(Project, verbose_name=_('project'))
    joined_at = models.DateTimeField(_('joined at'), auto_now_add=True)

    def __unicode__(self):
        return u"%s@%s" % (self.member, self.project)

    class Meta:
        unique_together = ('project', 'member')
      

class Milestone(models.Model):
    """
    """
    project = models.ForeignKey(Project, verbose_name=_('project'))
    name = models.CharField(max_length=64)
    slug = AutoSlugField(max_length=64, populate_from='name', always_update=True, unique_with='project')
    description = models.TextField()
    author = models.ForeignKey(User, verbose_name=_('author'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    deadline = models.DateField(_('deadline'), default=datetime.date.today() + datetime.timedelta(days=10))
    date_completed = models.DateField(_('date completed'), null=True, blank=True)

    class Meta:
        ordering = ('created_at',)
        verbose_name = _('milestone')
        verbose_name_plural = _('milestones')
        unique_together = ('project', 'name')

    def __unicode__(self):
        return self.name


class DictModel(models.Model):
    name = models.CharField(_('name'), max_length=32)
    description = models.TextField(_('description'), null=True, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True
        ordering = ('id',)


class OrderedDictModel(DictModel):
    """
    DictModel with order column and default ordering.
    """
    order = models.IntegerField(_('order'))

    class Meta:
        abstract = True
        ordering = ['order', 'name']


class Priority(OrderedDictModel):
    """
    """
    project = models.ForeignKey(Project)
    slug = AutoSlugField(max_length=64, populate_from='name', always_update=True, unique_with='project')

    class Meta:
        verbose_name = _('priority level')
        verbose_name_plural = _('priority levels')
        unique_together = ('project', 'name')
        
        
class Status(OrderedDictModel):
    """
    """
    project = models.ForeignKey(Project)
    is_resolved = models.BooleanField(verbose_name=_('is resolved'), default=False)
    is_initial = models.BooleanField(verbose_name=_('is initial'), default=False)
    destinations = models.ManyToManyField('self', verbose_name=_('destinations'), through='Transition', symmetrical=False, null=True, blank=True)
    slug = AutoSlugField(max_length=64, populate_from='name', always_update=True, unique_with='project')

    def can_change_to(self, new_status):
        """
        Checks if ``Transition`` object with ``source`` set to ``self`` and
        ``destination`` to given ``new_status`` exists.
        """
        try:
            Transition.objects.only('id')\
                .get(source__id=self.id, destination__id=new_status.id)
            return True
        except Transition.DoesNotExist:
            return False

    class Meta:
        verbose_name = _('status')
        verbose_name_plural = _('statuses')
        unique_together = ('project', 'name')
        ordering = ['order']

    def __unicode__(self):
        return self.name


class Transition(models.Model):
    """
    Instances allow to change source Status to destination Status.
    Needed for custom workflows.
    """
    source = models.ForeignKey(Status, verbose_name=_('source status'), related_name='sources')
    destination = models.ForeignKey(Status, verbose_name=_('destination status'))

    class Meta:
        verbose_name = _('transition')
        verbose_name_plural = _('transitions')
        unique_together = ('source', 'destination')

    def __unicode__(self):
        return u'%s->%s' % (self.source, self.destination)


class TaskType(OrderedDictModel):
    """
    """
    project = models.ForeignKey(Project)

    class Meta:
        verbose_name = _('task type')
        verbose_name_plural = _('task types')
        unique_together = ('project', 'name')
        
        
class Task(TaskMixin, models.Model):
    """
    """
    project = models.ForeignKey(Project, verbose_name=_('project'))
    
    author = models.ForeignKey(User, verbose_name=_('author'), related_name='created_tasks', blank=True)
    author_ip = models.IPAddressField(null=True, blank=True)
    
    owner = models.ForeignKey(User, verbose_name=_('owner'), related_name='owned_tasks', null=True, blank=True)

    summary = models.CharField(_('summary'), max_length=64)
    description = models.TextField(_('description'))
    
    status = models.ForeignKey(Status, verbose_name=_('status'))
    priority = models.ForeignKey(Priority, verbose_name=_('priority'))
    type = models.ForeignKey(TaskType, verbose_name=_('task type'))
    
    deadline = models.DateField(_('deadline'), null=True, blank=True, help_text='YYYY-MM-DD')
    milestone = models.ForeignKey(Milestone, verbose_name=_('milestone'), null=True, blank=True)
    component = models.ForeignKey(Component, verbose_name=_('component'))
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True, editable=False)

    edited_at = models.DateTimeField(_('edited at'), auto_now=True)
    editor = models.ForeignKey(User, verbose_name=_('editor'), blank=True,
        null=True)
    editor_ip = models.IPAddressField(null=True, blank=True)

    def __unicode__(self):
        return u'Task:%s' % (self.summary)


from follow import utils
import reversion

reversion.register(Task)

utils.register(User)

utils.register(Project)
utils.register(Milestone)
utils.register(Task)


