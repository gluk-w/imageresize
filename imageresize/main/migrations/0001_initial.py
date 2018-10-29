# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-10-31 01:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Thumbnail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hash', models.CharField(max_length=64, unique=True)),
                ('src', models.URLField()),
                ('result', models.FileField(upload_to='thumbnail')),
            ],
        ),
    ]
