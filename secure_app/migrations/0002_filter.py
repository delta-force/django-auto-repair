# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('secure_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Filter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url_path', models.CharField(max_length=50)),
                ('field_name', models.CharField(max_length=200, null=True)),
                ('regex_filter', models.CharField(max_length=200)),
            ],
        ),
    ]
