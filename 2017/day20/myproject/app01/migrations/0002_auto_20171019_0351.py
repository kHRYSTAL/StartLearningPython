# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-19 03:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='email',
            field=models.EmailField(default=123456, max_length=254),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userinfo',
            name='pwd',
            field=models.CharField(default=123456789, max_length=12),
            preserve_default=False,
        ),
    ]