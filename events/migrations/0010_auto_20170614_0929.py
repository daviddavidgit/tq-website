# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-14 09:29
from __future__ import unicode_literals

from django.db import migrations
import djangocms_text_ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0009_auto_20170614_0757'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventtranslation',
            name='description',
            field=djangocms_text_ckeditor.fields.HTMLField(blank=True, null=True, verbose_name='[TR] Description'),
        ),
    ]