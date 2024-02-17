# Generated by Django 5.0.2 on 2024-02-16 23:53

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("leaderboard", "0003_rename_time_ms_time_total_ms_time_penalties_ms"),
    ]

    operations = [
        migrations.CreateModel(
            name="Series",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=50)),
                ("slug", models.SlugField(unique=True)),
                ("order", models.IntegerField(default=0)),
                ("create_date", models.DateField(auto_now_add=True)),
                ("modify_date", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name="course",
            name="create_date",
            field=models.DateField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="course",
            name="modify_date",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name="course",
            name="slug",
            field=models.SlugField(),
        ),
        migrations.AlterField(
            model_name="time",
            name="total_ms",
            field=models.IntegerField(),
        ),
        migrations.AddField(
            model_name="course",
            name="series",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="leaderboard.series",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="course",
            unique_together={("series", "slug")},
        ),
    ]
