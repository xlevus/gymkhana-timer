# Generated by Django 4.0.5 on 2022-07-02 03:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rider', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='rider',
            name='_display_name',
            field=models.CharField(blank=True, db_column='display_name', default='', max_length=100),
        ),
    ]
