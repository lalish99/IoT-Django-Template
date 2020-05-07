from rest_framework import permissions
from rest_framework import exceptions
from users.models import CustomAccessTokens
from IoT import models

def owned_objects(token):
    """
    Returns token owned instances in a dictionary
    """
    owns = {
        'projects':[],
        'zones':[],
        'nodes':[],
        'sensors':[],
    }
    if isinstance(token, CustomAccessTokens):
        owns['projects'] = token.token_iot_projects.all()
        owned_zones = []
        for p in owns['projects']:
            owned_zones.extend(p.project_zones.all())
        owns['zones'] = owned_zones
        owns['zones'].extend(token.token_iot_zones.all())
        owned_nodes = []
        owned_sensors = []
        for z in owns['zones']:
            owned_nodes.extend(z.zone_nodes.all())
            owned_sensors.extend(z.zone_ambiental_sensors.all())
        owns['nodes'] = owned_nodes
        owns['nodes'].extend(token.token_iot_nodes.all())
        for n in owns['nodes']:
            owned_sensors.extend(n.node_sensors.all())
        owns['sensors'] = owned_sensors
        
    return owns

class IsProjectOwner(permissions.BasePermission):
    """
    Validates if the request user has project permissions
    ====
    This allows to manage every aspect of a project
    including child zones, nodes, sensors and measurements
    """
    def has_object_permission(self, request, view, obj):
        """
        A project is expected as the obj
        ====
        """
        if request.user.is_superuser and request.auth is None:
            return True
        token = request.auth
        owns = owned_objects(token)
        if isinstance(obj, models.Projects):
            return obj in owns['projects']
        elif isinstance(obj, models.Zones):
            return IsZoneOwner().has_object_permission(request,view,obj)
        raise exceptions.PermissionDenied(detail={'ERROR':'No project detected'}, code=403)


class IsZoneOwner(permissions.BasePermission):
    """
    Validates if the request user has zone permissions
    ====
    This allows to manage every aspect of a zone
    including child nodes, sensors and measurements
    """
    def has_object_permission(self, request, view, obj):
        """
        A zone is expected as the obj
        ====
        """
        if request.user.is_superuser and request.auth is None:
            return True
        token = request.auth
        owns = owned_objects(token)
        if isinstance(obj, models.Zones):
            return obj in owns['zones']
        elif isinstance(obj, models.Node):
            return IsNodeOwner().has_object_permission(request,view,obj)
        elif isinstance(obj, models.Sensors):
            return CanManageSensor().has_object_permission(request,view,obj)
        raise exceptions.PermissionDenied(detail={'ERROR':'No zone detected'}, code=403)


class IsNodeOwner(permissions.BasePermission):
    """
    Validates if the request user has node permissions
    ====
    This allows to manage every aspect of a node
    including child sensors, and measurements
    """
    def has_object_permission(self, request, view, obj):
        """
        A node is expected as the obj
        ====
        """
        if request.user.is_superuser and request.auth is None:
            return True
        token = request.auth
        owns = owned_objects(token)
        if isinstance(obj, models.Node):
            return obj in owns['nodes']
        elif isinstance(obj, models.Sensors):
            return CanManageSensor().has_object_permission(request,view,obj)
        raise exceptions.PermissionDenied(detail={'ERROR':'No node detected'}, code=403)


class CanManageSensor(permissions.BasePermission):
    """
    Validates if the request user can visualize a sensors information
    ====
    Not all users should be able to visualize a sensors information
    """
    def has_object_permission(self, request, view, obj):
        """
        A sensor is expected as the obj
        ====
        """
        if request.user.is_superuser and request.auth is None:
            return True
        token = request.auth
        owns = owned_objects(token)
        if isinstance(obj, models.Sensors):
            return obj in owns['sensors']
        raise exceptions.PermissionDenied(detail={'ERROR':'No sensor detected'}, code=403)
