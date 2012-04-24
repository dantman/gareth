# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Project'
        db.create_table('garethweb_project', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('garethweb', ['Project'])

        # Adding model 'Role'
        db.create_table('garethweb_role', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('role', self.gf('django.db.models.fields.CharField')(unique=True, max_length=20)),
        ))
        db.send_create_signal('garethweb', ['Role'])

        # Adding model 'User'
        db.create_table('garethweb_user', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('username', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('auth', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('garethweb', ['User'])

        # Adding M2M table for field roles on 'User'
        db.create_table('garethweb_user_roles', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(orm['garethweb.user'], null=False)),
            ('role', models.ForeignKey(orm['garethweb.role'], null=False))
        ))
        db.create_unique('garethweb_user_roles', ['user_id', 'role_id'])

        # Adding model 'UserEmail'
        db.create_table('garethweb_useremail', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['garethweb.User'])),
            ('email', self.gf('django.db.models.fields.EmailField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('garethweb', ['UserEmail'])

        # Adding model 'UnconfirmedUserEmail'
        db.create_table('garethweb_unconfirmeduseremail', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['garethweb.User'])),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=255)),
            ('token', self.gf('django.db.models.fields.CharField')(max_length=64, db_index=True)),
        ))
        db.send_create_signal('garethweb', ['UnconfirmedUserEmail'])

        # Adding model 'Remote'
        db.create_table('garethweb_remote', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['garethweb.Project'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['garethweb.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('garethweb', ['Remote'])

    def backwards(self, orm):
        # Deleting model 'Project'
        db.delete_table('garethweb_project')

        # Deleting model 'Role'
        db.delete_table('garethweb_role')

        # Deleting model 'User'
        db.delete_table('garethweb_user')

        # Removing M2M table for field roles on 'User'
        db.delete_table('garethweb_user_roles')

        # Deleting model 'UserEmail'
        db.delete_table('garethweb_useremail')

        # Deleting model 'UnconfirmedUserEmail'
        db.delete_table('garethweb_unconfirmeduseremail')

        # Deleting model 'Remote'
        db.delete_table('garethweb_remote')

    models = {
        'garethweb.project': {
            'Meta': {'object_name': 'Project'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'garethweb.remote': {
            'Meta': {'object_name': 'Remote'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['garethweb.Project']"}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['garethweb.User']"})
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