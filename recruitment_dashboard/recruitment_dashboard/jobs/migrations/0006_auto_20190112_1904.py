# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2019-01-12 13:34
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0005_remove_recruiter_uname'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobdetails',
            name='jobcreatedate',
            field=models.DateField(default=datetime.date(2019, 1, 12)),
        ),
        migrations.AlterUniqueTogether(
            name='jobdetails',
            unique_together=set([('clientname', 'positionname')]),
        ),
        migrations.AlterUniqueTogether(
            name='profiledetails',
            unique_together=set([('resourcename', 'resourcemail')]),
        ),
    ]
