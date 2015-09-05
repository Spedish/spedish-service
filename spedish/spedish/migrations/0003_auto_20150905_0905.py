# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spedish', '0002_auto_20150905_0837'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='line_two',
            field=models.CharField(max_length=100, blank=True),
        ),
    ]
