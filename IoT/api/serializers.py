from rest_framework.exceptions import ParseError
from django.shortcuts import get_object_or_404
from rest_framework import routers, serializers, viewsets
from IoT.models import Projects, Zones, Node, Sensors, Measurement

"""
Single class serializers
"""
class ProjectsSerializer(serializers.ModelSerializer):
    """
    Serializer for Projects model
    """
    class Meta:
        model = Projects
        fields = ('id', 'name', 'description')


class ZonesSerializer(serializers.ModelSerializer):
    """
    Serializer for Zones model
    """
    id_project = serializers.IntegerField(source="project.id", read_only=False)
    class Meta:
        model = Zones
        fields = ('id', 'name', 'description', 'id_project')
    
    def create(self, validated_data):
        if 'project' not in validated_data:
            raise ParseError(detail='Project missing in validated data', code=404)
        project = validated_data.pop('project')
        if 'id' not in project:
            raise ParseError(detail='Project id missing', code=404)
        project = get_object_or_404(Projects,pk=project['id'])
        zone = Zones(project=project, **validated_data)
        zone.save()
        return zone


class NodeSerializer(serializers.ModelSerializer):
    """
    Serializer for Node model
    """
    id_zone = serializers.IntegerField(source="zone.id", read_only=True)
    class Meta:
        model = Node
        fields = ('id', 'name', 'description', 'id_zone')


class SensorsSerializer(serializers.ModelSerializer):
    """
    Serializer for Sensors model
    """
    id_node = serializers.IntegerField(source="node.id", read_only=True, required=False)
    class Meta:
        model = Sensors
        fields = ('id', 'ambiental', 'sensor_type', 'id_node')


class MeasurementSerializer(serializers.ModelSerializer):
    """
    Serializer for Measurement model
    """
    id_sensor = serializers.IntegerField(source="sensor.id")
    class Meta:
        model = Measurement
        fields = ('id', 'value', 'created_at', 'id_sensor', 'measurement_type')
        extra_kwargs = {
            'id': {'read_only': True},
            'created_at': {'read_only': True},
            }
    
    def create(self, validated_data):
        """
        Modified creation of measurement
        """
        id_sensor = validated_data.get('sensor', None).get('id', None)
        if id_sensor is None:
            raise serializers.ValidationError("id_sensor missing")
        del validated_data['sensor']
        try:
            sensor = Sensors.objects.get(pk=id_sensor)
        except:
            raise serializers.ValidationError("Sensor with id {} does not exist".format(id_sensor))

        m = Measurement(sensor=sensor, **validated_data)
        m.save()
        return m

            
"""
Nested serializers
"""
class NestedSensorSerializer(serializers.ModelSerializer):
    """
    Nested sensor serializer
    ====
    Manages sensor measurements
    """
    measurements = MeasurementSerializer(many=True, read_only=True, source='sensor_measurements')
    id_node = serializers.IntegerField(source="node.id", read_only=True)
    class Meta:
        model = Sensors
        fields = ('id', 'ambiental', 'sensor_type', 'id_node', 'measurements')


class NestedNodeSerializer(serializers.ModelSerializer):
    """
    Nested node serializer
    ====
    This serializer includes The sensor nodes
    """
    sensors = SensorsSerializer(many=True, read_only=True, source='node_sensors')
    id_zone = serializers.IntegerField(source="zone.id", read_only=True)
    class Meta:
        model = Node
        fields = ['id', 'name', 'description', 'sensors','id_zone']


class NestedZoneSerializer(serializers.ModelSerializer):
    """
    Nested Zone serializer
    ====
    Node containing ambiental sensors and nodes
    with their respective sensors
    """
    ambiental = SensorsSerializer(many=True, read_only=True, source='ambiental_sensors')
    nodes = NestedNodeSerializer(many=True, read_only=True, source='zone_nodes')
    id_project = serializers.IntegerField(source="project.id")
    
    class Meta:
        model = Zones
        fields = ['id', 'nodes', 'ambiental', 'name', 'description', 'id_project']


class NestedProjectsSerializer(serializers.ModelSerializer):
    """
    Nested projects serializer
    ====
    """
    zones = NestedZoneSerializer(many=True, read_only=True, source='project_zones')

    class Meta:
        model = Projects
        fields = ['id', 'name', 'description', 'zones']