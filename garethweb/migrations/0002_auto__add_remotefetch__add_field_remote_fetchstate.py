# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'RemoteFetch'
        db.create_table('garethweb_remotefetch', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('started_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('completed_at', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('status', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('compressing_objects', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('receiving_objects', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('resolving_deltas', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
        ))
        db.send_create_signal('garethweb', ['RemoteFetch'])

        # Adding field 'Remote.fetchstate'
        db.add_column('garethweb_remote', 'fetchstate',
                      self.gf('django.db.models.fields.related.OneToOneField')(to=orm['garethweb.RemoteFetch'], unique=True, null=True),
                      keep_default=False)

    def backwards(self, orm):
        # Deleting model 'RemoteFetch'
        db.delete_table('garethweb_remotefetch')

        # Deleting field 'Remote.fetchstate'
        db.delete_column('garethweb_remote', 'fetchstate_id')

    models = {
        'garethweb.project': {
            'Meta': {'object_name': 'Project'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'garethweb.remote': {
            'Meta': {'object_name': 'Remote'},
            'fetchstate': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['garethweb.RemoteFetch']", 'unique': 'True', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['garethweb.Project']"}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['garethweb.User']"})
        },
        'garethweb.remotefetch': {
            'Meta': {'object_name': 'RemoteFetch'},
            'completed_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'compressing_objects': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'receiving_objects': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'resolving_deltas': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'started_at': ('django.db.models.fields.DateTimeField', [], {}),
            'status': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'})
        },
        'garethweb.role': {
            'Meta': {'object_name': 'Role'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'role': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'})
        },
        'garethweb.unconfirmeduseremail': {
            'Meta': {'object_name': 'UnconfirmedUserEmail'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'token': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['garethweb.User']"})
        },
        'garethweb.user': {
            'Meta': {'object_name': 'User'},
            'auth': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'roles': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['garethweb.Role']", 'symmetrical': 'False'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'garethweb.useremail': {
            'Meta': {'object_name': 'UserEmail'},
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['garethweb.User']"})
        }
    }

    complete_apps = ['garethweb']