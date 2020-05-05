from django.db import models
from users.models import GeneralUser, CustomAccessTokens
import IoT.model_choices as choices

class Projects(models.Model):
    """
    Class that stores detailed information
    on models
    ====
    """
    name = models.CharField(max_length=20)
    description = models.TextField()
    
    snippet_title = models.CharField(max_length=30)
    snippet_image = models.TextField()

    user = models.ForeignKey(
        GeneralUser,
        on_delete=models.CASCADE,
        related_name="user_iot_projects",
    )
    access_keys = models.ManyToManyField(
        CustomAccessTokens,
        blank=True,
        related_name="token_iot_projects"
    )

    def __str__(self):
        return '{}: {}'.format(self.name, self.snippet_title)

class Zones(models.Model):
    """
    Class that manages information related
    to data collection zones.
    ====
    
    The idea is to manage in a simple way different
    kind of sensors and to be able to store relevant
    information to the space were the sensors are
    or what are they monitoring     
    """
    project = models.ForeignKey(
        Projects,
        on_delete=models.CASCADE,
        related_name="project_zones",
    )
    access_keys = models.ManyToManyField(
        CustomAccessTokens,
        blank=True,
        related_name="token_iot_zones"
    )
    name = models.CharField(max_length=30)
    description = models.TextField()

    def __str__(self):
        return '{} from {}'.format(self.name, self.project.name)

    def ambiental_sensors(self):
        return Sensors.objects.filter(zone=self, ambiental=True)


class Node(models.Model):
    """
    Class dedicated to manage the arrangement of
    sensors in a zone
    ====
    """
    name = models.CharField(max_length=20)
    description = models.TextField()
    zone = models.ForeignKey(
        Zones,
        on_delete=models.CASCADE,
        related_name="zone_nodes",
    )
    access_keys = models.ManyToManyField(
        CustomAccessTokens,
        blank=True,
        related_name="token_iot_nodes"
    )
    def __str__(self):
        return '{} from {}'.format(self.name, self.zone.name)


class Sensors(models.Model):
    """
    Class dedicated to manage and store incomming
    information from in-field sensors
    ====
    """

    ambiental = models.BooleanField()
    sensor_type = models.CharField(
        max_length=10,
        choices=choices.SENSOR_TYPE_CHOICES,
        blank=False,
        null=False
    )
    node = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name="node_sensors",
        blank=True,
        null=True,
        default=None
    )
    zone = models.ForeignKey(
        Zones,
        on_delete=models.CASCADE,
        related_name="zone_ambiental_sensors",
    )
    def __str__(self):
        return '{} from {}'.format(self.sensor_type, self.zone.name)


class Measurement(models.Model):
    """
    Class to store and keep a register of
    sensor data captures
    ====
    """
    measurement_type = models.CharField(
        max_length=20,
        choices=choices.MEASUREMENT_TYPE_CHOICES,
        blank=False,
        null=False
    )
    value = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    sensor = models.ForeignKey(
        Sensors,
        on_delete=models.CASCADE,
        related_name="sensor_measurements",
    )
    def __str__(self):
        return '{}:{} from {}'.format(self.created_at, self.value, self.sensor.sensor_type)
