# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2019-06-06 10:38
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pipeline', '0020_logentry'),
    ]

    operations = [
        migrations.DeleteModel(
            name='LogEntry',
        ),
    ]