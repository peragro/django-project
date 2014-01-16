# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Project'
        db.create_table(u'django_project_project', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique_with=('author',), max_length=128, populate_from='name')),
            (u'author', self.gf('django.db.models.fields.related.ForeignKey')(related_name='created_projects', to=orm['auth.User'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'django_project', ['Project'])

        # Adding model 'Component'
        db.create_table(u'django_project_component', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['django_project.Project'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique_with=('project',), max_length=64, populate_from='name')),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'django_project', ['Component'])

        # Adding unique constraint on 'Component', fields ['project', 'name']
        db.create_unique(u'django_project_component', ['project_id', 'name'])

        # Adding model 'Membership'
        db.create_table(u'django_project_membership', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('member', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['django_project.Project'])),
            ('joined_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'django_project', ['Membership'])

        # Adding unique constraint on 'Membership', fields ['project', 'member']
        db.create_unique(u'django_project_membership', ['project_id', 'member_id'])

        # Adding model 'Milestone'
        db.create_table(u'django_project_milestone', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['django_project.Project'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique_with=('project',), max_length=64, populate_from='name')),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('deadline', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2014, 1, 26, 0, 0))),
            ('date_completed', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'django_project', ['Milestone'])

        # Adding unique constraint on 'Milestone', fields ['project', 'name']
        db.create_unique(u'django_project_milestone', ['project_id', 'name'])

        # Adding model 'Priority'
        db.create_table(u'django_project_priority', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['django_project.Project'])),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique_with=('project',), max_length=64, populate_from='name')),
        ))
        db.send_create_signal(u'django_project', ['Priority'])

        # Adding unique constraint on 'Priority', fields ['project', 'name']
        db.create_unique(u'django_project_priority', ['project_id', 'name'])

        # Adding model 'Status'
        db.create_table(u'django_project_status', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['django_project.Project'])),
            ('is_resolved', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_initial', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique_with=('project',), max_length=64, populate_from='name')),
        ))
        db.send_create_signal(u'django_project', ['Status'])

        # Adding unique constraint on 'Status', fields ['project', 'name']
        db.create_unique(u'django_project_status', ['project_id', 'name'])

        # Adding model 'Transition'
        db.create_table(u'django_project_transition', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sources', to=orm['django_project.Status'])),
            ('destination', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['django_project.Status'])),
        ))
        db.send_create_signal(u'django_project', ['Transition'])

        # Adding unique constraint on 'Transition', fields ['source', 'destination']
        db.create_unique(u'django_project_transition', ['source_id', 'destination_id'])

        # Adding model 'TaskType'
        db.create_table(u'django_project_tasktype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['django_project.Project'])),
        ))
        db.send_create_signal(u'django_project', ['TaskType'])

        # Adding unique constraint on 'TaskType', fields ['project', 'name']
        db.create_unique(u'django_project_tasktype', ['project_id', 'name'])

        # Adding model 'Task'
        db.create_table(u'django_project_task', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['django_project.Project'])),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(related_name='created_tasks', blank=True, to=orm['auth.User'])),
            ('author_ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15, blank=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='owned_tasks', null=True, to=orm['auth.User'])),
            ('summary', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('status', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['django_project.Status'])),
            ('priority', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['django_project.Priority'])),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['django_project.TaskType'])),
            ('deadline', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('milestone', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['django_project.Milestone'], null=True, blank=True)),
            ('component', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['django_project.Component'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('edited_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('editor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('editor_ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15, blank=True)),
        ))
        db.send_create_signal(u'django_project', ['Task'])


    def backwards(self, orm):
        # Removing unique constraint on 'TaskType', fields ['project', 'name']
        db.delete_unique(u'django_project_tasktype', ['project_id', 'name'])

        # Removing unique constraint on 'Transition', fields ['source', 'destination']
        db.delete_unique(u'django_project_transition', ['source_id', 'destination_id'])

        # Removing unique constraint on 'Status', fields ['project', 'name']
        db.delete_unique(u'django_project_status', ['project_id', 'name'])

        # Removing unique constraint on 'Priority', fields ['project', 'name']
        db.delete_unique(u'django_project_priority', ['project_id', 'name'])

        # Removing unique constraint on 'Milestone', fields ['project', 'name']
        db.delete_unique(u'django_project_milestone', ['project_id', 'name'])

        # Removing unique constraint on 'Membership', fields ['project', 'member']
        db.delete_unique(u'django_project_membership', ['project_id', 'member_id'])

        # Removing unique constraint on 'Component', fields ['project', 'name']
        db.delete_unique(u'django_project_component', ['project_id', 'name'])

        # Deleting model 'Project'
        db.delete_table(u'django_project_project')

        # Deleting model 'Component'
        db.delete_table(u'django_project_component')

        # Deleting model 'Membership'
        db.delete_table(u'django_project_membership')

        # Deleting model 'Milestone'
        db.delete_table(u'django_project_milestone')

        # Deleting model 'Priority'
        db.delete_table(u'django_project_priority')

        # Deleting model 'Status'
        db.delete_table(u'django_project_status')

        # Deleting model 'Transition'
        db.delete_table(u'django_project_transition')

        # Deleting model 'TaskType'
        db.delete_table(u'django_project_tasktype')

        # Deleting model 'Task'
        db.delete_table(u'django_project_task')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'django_project.component': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('project', 'name'),)", 'object_name': 'Component'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['django_project.Project']"}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': "('project',)", 'max_length': '64', 'populate_from': "'name'"})
        },
        u'django_project.membership': {
            'Meta': {'unique_together': "(('project', 'member'),)", 'object_name': 'Membership'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'joined_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['django_project.Project']"})
        },
        u'django_project.milestone': {
            'Meta': {'ordering': "('created_at',)", 'unique_together': "(('project', 'name'),)", 'object_name': 'Milestone'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_completed': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'deadline': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2014, 1, 26, 0, 0)'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['django_project.Project']"}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': "('project',)", 'max_length': '64', 'populate_from': "'name'"})
        },
        u'django_project.priority': {
            'Meta': {'unique_together': "(('project', 'name'),)", 'object_name': 'Priority'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['django_project.Project']"}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': "('project',)", 'max_length': '64', 'populate_from': "'name'"})
        },
        u'django_project.project': {
            'Meta': {'object_name': 'Project'},
            u'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'created_projects'", 'to': u"orm['auth.User']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'through': u"orm['django_project.Membership']", 'symmetrical': 'False'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': "('author',)", 'max_length': '128', 'populate_from': "'name'"})
        },
        u'django_project.status': {
            'Meta': {'ordering': "['order']", 'unique_together': "(('project', 'name'),)", 'object_name': 'Status'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'destinations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['django_project.Status']", 'null': 'True', 'through': u"orm['django_project.Transition']", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_initial': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_resolved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['django_project.Project']"}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': "('project',)", 'max_length': '64', 'populate_from': "'name'"})
        },
        u'django_project.task': {
            'Meta': {'object_name': 'Task'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'created_tasks'", 'blank': 'True', 'to': u"orm['auth.User']"}),
            'author_ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'blank': 'True'}),
            'component': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['django_project.Component']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deadline': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'edited_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'editor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'editor_ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'milestone': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['django_project.Milestone']", 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'owned_tasks'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'priority': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['django_project.Priority']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['django_project.Project']"}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['django_project.Status']"}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['django_project.TaskType']"})
        },
        u'django_project.tasktype': {
            'Meta': {'unique_together': "(('project', 'name'),)", 'object_name': 'TaskType'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['django_project.Project']"})
        },
        u'django_project.transition': {
            'Meta': {'unique_together': "(('source', 'destination'),)", 'object_name': 'Transition'},
            'destination': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['django_project.Status']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sources'", 'to': u"orm['django_project.Status']"})
        }
    }

    complete_apps = ['django_project']