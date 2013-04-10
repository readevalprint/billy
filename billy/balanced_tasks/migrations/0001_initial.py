# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TaskRunner'
        db.create_table(u'balanced_tasks_taskrunner', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('frequency', self.gf('django.db.models.fields.CharField')(default='', max_length=20, blank=True)),
            ('task_id', self.gf('django.db.models.fields.CharField')(default='', max_length=36, blank=True)),
            ('last_run', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('is_deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'balanced_tasks', ['TaskRunner'])

        # Adding model 'AuditFeed'
        db.create_table(u'balanced_tasks_auditfeed', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'balanced_tasks', ['AuditFeed'])

        # Adding model 'AuditEvent'
        db.create_table(u'balanced_tasks_auditevent', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('feed', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['balanced_tasks.AuditFeed'])),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'balanced_tasks', ['AuditEvent'])

        # Adding model 'DebitTask'
        db.create_table(u'balanced_tasks_debittask', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('runner', self.gf('annoying.fields.AutoOneToOneField')(related_name='balanced_task', unique=True, to=orm['balanced_tasks.TaskRunner'])),
            ('audit_feed', self.gf('annoying.fields.AutoOneToOneField')(related_name='balanced_task', unique=True, to=orm['balanced_tasks.AuditFeed'])),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('is_deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('card', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['django_balanced.Card'])),
            ('amount', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
        ))
        db.send_create_signal(u'balanced_tasks', ['DebitTask'])


    def backwards(self, orm):
        # Deleting model 'TaskRunner'
        db.delete_table(u'balanced_tasks_taskrunner')

        # Deleting model 'AuditFeed'
        db.delete_table(u'balanced_tasks_auditfeed')

        # Deleting model 'AuditEvent'
        db.delete_table(u'balanced_tasks_auditevent')

        # Deleting model 'DebitTask'
        db.delete_table(u'balanced_tasks_debittask')


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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'balanced_tasks.auditevent': {
            'Meta': {'object_name': 'AuditEvent'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'feed': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['balanced_tasks.AuditFeed']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {})
        },
        u'balanced_tasks.auditfeed': {
            'Meta': {'object_name': 'AuditFeed'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'balanced_tasks.debittask': {
            'Meta': {'object_name': 'DebitTask'},
            'amount': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'audit_feed': ('annoying.fields.AutoOneToOneField', [], {'related_name': "'balanced_task'", 'unique': 'True', 'to': u"orm['balanced_tasks.AuditFeed']"}),
            'card': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['django_balanced.Card']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'runner': ('annoying.fields.AutoOneToOneField', [], {'related_name': "'balanced_task'", 'unique': 'True', 'to': u"orm['balanced_tasks.TaskRunner']"})
        },
        u'balanced_tasks.taskrunner': {
            'Meta': {'object_name': 'TaskRunner'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'frequency': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_run': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'task_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '36', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'django_balanced.card': {
            'Meta': {'object_name': 'Card', 'db_table': "u'balanced_cards'"},
            'brand': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {}),
            'expiration_month': ('django.db.models.fields.IntegerField', [], {}),
            'expiration_year': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'last_four': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'uri': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'cards'", 'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['balanced_tasks']