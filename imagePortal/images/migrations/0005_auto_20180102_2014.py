# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-02 20:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0004_auto_20180102_2013'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]
