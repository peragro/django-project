from django.contrib.auth.models import User, AnonymousUser, Group
from django.core.urlresolvers import reverse
from django.test import TestCase

from django_project.models import Project, Task, Status, Transition, Component, Priority, TaskType

from django_project import signals


from django.conf import settings
from django.db.models import loading


from django.db import models
from django_project.managers import ObjectTaskMixin

class Asset(ObjectTaskMixin):
    title = models.CharField(max_length=128)

    def __unicode__(self):
        return self.title

class ProjectTest(TestCase):
    initiated = False

    @classmethod
    def setUpClass(cls, *args, **kwargs):
        if not cls.initiated:
            cls.create_models_from_app('django_project.tests')
            cls.initiated = True

        super(ProjectTest, cls).setUpClass(*args, **kwargs)

    @classmethod
    def create_models_from_app(cls, app_name):
        """
        Manually create Models (used only for testing) from the specified string app name.
        Models are loaded from the module "<app_name>.models"
        """
        from django.db import connection, DatabaseError
        from django.db.models.loading import load_app

        app = load_app(app_name)
        from django.core.management import sql
        from django.core.management.color import no_style
        sql = sql.sql_create(app, no_style(), connection)
        cursor = connection.cursor()
        for statement in sql:
            try:
                cursor.execute(statement)
            except DatabaseError, excn:
                print excn.message

    def setUp(self):
        self.author = User.objects.create(username='Test User')
        self.project = Project.objects.create(name='Test Project', author=self.author)
        
        self.priority = Priority.objects.create(project=self.project, order=1, name='minor')
        self.component = Component.objects.create(project=self.project, name='Animation')
        self.type = TaskType.objects.create(project=self.project, order=1, name='Task')
        
        self.state_new = Status.objects.create(project=self.project, order=1, name='new', is_initial=True)
        self.state_pro = Status.objects.create(project=self.project, order=2, name='in progress', is_initial=True)
        self.state_pub = Status.objects.create(project=self.project, order=3, name='published', is_resolved=True)
        
        self.transition1 = Transition.objects.create(source=self.state_new, destination=self.state_pro)
        self.transition2 = Transition.objects.create(source=self.state_pro, destination=self.state_pro)
        self.transition3 = Transition.objects.create(source=self.state_pro, destination=self.state_pub)
        
        self.task = self.create_task('summary', 'description')


    def create_task(self, summary, description):
        task = Task.objects.create(project=self.project, author=self.author, summary=summary, description=description, 
                                        priority=self.priority,
                                        component=self.component,
                                        type=self.type,
                                        status=self.state_new)
        return task


    def test_signals(self):
        Handler = type('Handler', (object,), {
            'inc': lambda self: setattr(self, 'i', getattr(self, 'i') + 1),
            'i': 0
        })
        transition_handler_c = Handler()
        resolved_handler_c = Handler()
        new_handler_c = Handler()
        
        def transition_handler(signal, sender, instance, transition, old_state, new_state):
            self.assertEqual(sender, Task)
            self.assertEqual(instance, self.task)
            self.assertEqual(transition_handler.transition, transition)
            transition_handler_c.inc()
        
        def resolved_handler(signal, sender, instance, transition, old_state, new_state):
            self.assertEqual(sender, Task)
            self.assertEqual(instance, self.task)
            resolved_handler_c.inc()
            
        def new_handler(signal, sender, instance, transition, old_state, new_state):
            self.assertEqual(sender, Task)
            new_handler_c.inc()

        
        signals.workflow_task_transition.connect(transition_handler, dispatch_uid='transition')
        signals.workflow_task_resolved.connect(resolved_handler, dispatch_uid='resolved')
        signals.workflow_task_resolved.connect(new_handler, dispatch_uid='new')
        
        transition_handler.transition = self.transition1
        
        self.task.status = self.state_pro
        self.task.save()
        
        transition_handler.transition = self.transition2
        
        self.task.status = self.state_pro
        self.task.save()
        
        transition_handler.transition = self.transition3
        
        self.task.status = self.state_pub
        self.task.save()

        self.create_task('new task', 'description')

        self.assertEqual(2, transition_handler_c.i)
        self.assertEqual(1, resolved_handler_c.i)
        self.assertEqual(1, new_handler_c.i)
       
       
    def test_revisions(self): 
        self.task.description = 'revision 1'
        self.task.status = self.state_pro
        self.task.save_revision(self.author, 'comment 1')
        
        self.task.description = 'revision 2'
        self.task.save_revision(self.author, 'comment 2')
        
        self.assertEqual(2, self.task.nr_of_versions())
        
        versions = self.task.versions()
        self.assertEqual('comment 2', versions[0].revision.comment)
        self.assertEqual('comment 1', versions[1].revision.comment)
        
        self.assertEqual('revision 2', versions[0].field_dict['description'])
        self.assertEqual('revision 1', versions[1].field_dict['description'])
        
        self.assertEqual(self.author, versions[0].revision.user)
        self.assertEqual(self.author, versions[1].revision.user)
        
        
        self.assertEqual('revision 2', self.task.description)
        # Revert and refresh
        versions[1].revert()
        self.task = Task.objects.get(id=self.task.id)
        self.assertEqual('revision 1', self.task.description)

    def test_task_manager(self):    
        asset = Asset.objects.create(title="gg")
        asset.save()
        print asset.tasks
        asset.add_task(self.task)
        print asset.tasks.all()
        asset.add_task(self.task)
        print asset.tasks.all()
        
        #print dir(self.task)
        print asset.tasks_for_author(self.task.author)
        
        asset.remove_task(self.task)
        print asset.tasks.all()
