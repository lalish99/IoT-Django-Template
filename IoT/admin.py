from django.contrib import admin
from IoT import models

# Register your models here.
admin.site.register(models.Projects)
admin.site.register(models.Zones)
admin.site.register(models.Node)
admin.site.register(models.Sensors)