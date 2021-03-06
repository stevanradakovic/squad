# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-27 19:17
from __future__ import unicode_literals

from django.db import migrations
from django.utils import timezone
from squad.core.statistics import geomean
from squad.core.models import TestSummary


def create_or_update_projectstatus(apps, schema_editor):
    ProjectStatus = apps.get_model('core', 'ProjectStatus')
    Build = apps.get_model('core', 'Build')
    Metric = apps.get_model('core', 'Metric')
    for build in Build.objects.order_by('datetime').prefetch_related('status'):
        try:
            status = build.status
        except ProjectStatus.DoesNotExist:
            previous = ProjectStatus.objects.filter(
                build__project=build.project,
                build__datetime__lt=build.datetime,
            ).last()
            status = ProjectStatus(build=build, previous=previous)

        metrics = Metric.objects.filter(test_run__build_id=build.id).all()
        metrics_summary = geomean([m.result for m in metrics])

        test_summary = TestSummary(build)

        status.tests_pass = test_summary.tests_pass
        status.tests_fail = test_summary.tests_fail
        status.tests_skip = test_summary.tests_skip
        status.metrics_summary = metrics_summary
        status.last_updated = timezone.now()
        status.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0051_build_status'),
    ]

    operations = [
        migrations.RunPython(
            create_or_update_projectstatus,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
