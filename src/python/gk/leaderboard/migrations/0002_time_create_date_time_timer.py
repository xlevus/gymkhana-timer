# Generated by Django 4.0.4 on 2022-05-24 10:24

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("timer", "0002_alter_timer_owner"),
        ("leaderboard", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="time",
            name="create_date",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="time",
            name="timer",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="timer.timer",
            ),
        ),
    ]
