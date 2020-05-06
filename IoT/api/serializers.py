from rest_framework.exceptions import ParseError
from django.shortcuts import get_object_or_404
from rest_framework import routers, serializers, viewsets
from IoT.models import Projects, Zones, Node, Sensors, Measurement
from users.models import CustomAccessTokens

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
    id_project = serializers.IntegerField(source="project.id", read_only=False, required=False)
    class Meta:
        model = Zones
        fields = ('id', 'name', 'description', 'id_project')
    
    def create(self, validated_data):
        if 'project' not in self.context:
            raise ParseError(detail='Project missing in context', code=404)
        project = self.context['project']
        zone = Zones(project=project, **validated_data)
        zone.save()
        if 'token' in self.context and isinstance(self.context['token'], CustomAccessTokens):
            token = self.context['token']
            try:
                zone.access_keys.add(token)
            except Exception as e:
                print(e)
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

    def create(self, validated_data):
        if 'zone' not in self.context:
            raise ParseError(detail='Zone missing in context', code=404)
        zone = self.context['zone']
        node = Node(zone=zone, **validated_data)
        node.save()
        if 'token' in self.context and isinstance(self.context['token'], CustomAccessTokens):
            token = self.context['token']
            try:
                node.access_keys.add(token)
            except Exception as e:
                print(e)
        node.save()
        return node


class SensorsSerializer(serializers.ModelSerializer):
    """
    Serializer for Sensors model
    """
    id_node = serializers.IntegerField(source="node.id", read_only=True, required=False)
    class Meta:
        model = Sensors
        fields = ('id', 'ambiental', 'sensor_type', 'id_node')

    def create(self, validated_data):
        if 'zone' not in self.context:
            raise ParseError(detail='Zone missing in context', code=404)
        zone = self.context['zone']
        sensor = Sensors(zone=zone, **validated_data)
        if 'node' in self.context:
            node = self.context['node']
            sensor.node = node
        sensor.save()
        return sensor

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