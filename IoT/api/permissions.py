from rest_framework import permissions
from rest_framework import exceptions
from IoT import models

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
        if isinstance(obj, models.Projects):
            token = request.auth
            if token:
                if obj in token.token_iot_projects.all():
                    return True
            else:
                if obj in request.user.user_iot_projects.all():
                    return True
            return False
        elif isinstance(obj, models.Node):
            return IsNodeOwner().has_object_permission(request,view,obj)
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
        if isinstance(obj, models.Zones):
            token = request.auth
            if obj in token.token_iot_zones.all():
                return True
            return False
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
        if isinstance(obj, models.Node):
            token = request.auth
            if obj in token.token_iot_nodes.all():
                return True
            return False
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
        if isinstance(obj, models.Sensors):
            allowed_sensors = set()
            for p in request.user.user_iot_projects.all():
                for z in p.project_zones.all():
                    allowed_sensors.update(z.zone_ambiental_sensors.all())
            try:
                token = request.auth
                for p in tokn.token_iot_projects.all():
                    for z in p.project_zones.all():
                        allowed_sensors.update(z.zone_ambiental_sensors.all())
                for z in token.token_iot_zones.all():
                    allowed_sensors.update(z.zone_ambiental_sensors.all())
                for n in token.token_iot_nodes.all():
                    allowed_sensors.update(n.node_sensors.all())
            except:
                pass
            if obj in allowed_sensors:
                return True
            return False
        raise exceptions.PermissionDenied(detail={'ERROR':'No sensor detected'}, code=403)
