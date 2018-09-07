# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('helios', '0012_auto_20180720_1316'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='poll',
            options={'ordering': ('linked_ref', 'index', 'created_at')},
        ),
        migrations.RemoveField(
            model_name='election',
            name='linked_polls',
        ),
        migrations.RemoveField(
            model_name='poll',
            name='link_id',
        ),
        migrations.AlterField(
            model_name='poll',
            name='linked_ref',
            field=models.CharField(default=None, max_length=255, null=True, verbose_name='Poll reference id'),
            preserve_default=True,
        ),
    ]
