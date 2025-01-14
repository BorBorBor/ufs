# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-11-23 16:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0003_add_sort_order_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='list',
            name='sort_order',
            field=models.CharField(choices=[('Al', 'Alphabetical'), ('Ca', 'Callsign'), ('Co', 'Total consumption'), ('Ra', 'Random'), ('Lt', 'Last 30 days usage')], default='Al', max_length=2, verbose_name='account sort order'),
        ),
    ]
