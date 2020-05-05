# Generated by Django 3.0.5 on 2020-05-05 05:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('IoT', '0003_remove_projects_url_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sensors',
            name='sensor_type',
            field=models.CharField(choices=[('DHT11', 'Multisensor DHT11'), ('DHT22', 'Multisensor DHT22'), ('MCP9701A', 'Temperature sensor MCP9701A'), ('LDR', 'Photoresistor'), ('BME280', 'Pressure temperature humidity sensor BME280'), ('BMP180', 'Pressure temperature altitude sensor BMP180'), ('SM150', 'Moisture sensor'), ('CMS', 'Cable moisture sensor')], max_length=10),
        ),
    ]