# Generated by Django 3.0.5 on 2020-05-05 04:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('IoT', '0002_auto_20200504_2006'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projects',
            name='url_name',
        ),
    ]