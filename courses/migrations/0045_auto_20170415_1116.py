# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-15 11:16
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0044_auto_20170415_1106'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bankaccount',
            old_name='city',
            new_name='bank_city',
        ),
        migrations.RenameField(
            model_name='bankaccount',
            old_name='zip_code',
            new_name='bank_zip_code',
        ),
    ]