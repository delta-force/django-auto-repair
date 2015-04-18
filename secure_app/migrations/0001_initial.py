# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.IntegerField(default=0)),
                ('full_url', models.CharField(max_length=200)),
                ('host', models.CharField(max_length=50)),
                ('url_path', models.CharField(max_length=50)),
                ('is_good', models.BooleanField(default=True)),
                ('param_map', jsonfield.fields.JSONField()),
            ],
        ),
    ]
