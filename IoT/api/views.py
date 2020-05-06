from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from rest_framework.authentication import  BasicAuthentication
from users.api.cauth import CAccessTokenRestAuth
from users.models import GeneralUser
from django.http import Http404
import IoT.api.serializers as serializers
import IoT.models as models
import IoT.api.permissions as IoTPermissions
import json

class IoTProjectsViewSet(viewsets.ViewSet):
    """
    General IoT project api conncetions managment.
    """
    authentication_classes = (BasicAuthentication,CAccessTokenRestAuth, )

    """
    ============
    Projects
    ============
    """

    @action(detail=False, methods=["get"], permission_classes=(permissions.IsAuthenticated,))
    def projects(self, request):
        """
        ## Obtain all user's projects
        ====

        #### Projects can't be created within the API they most be created from within the
        admin console.

        #### Allowed methods:
        * #### *GET*: View projects vinculated to user
        """
        if not request.user.is_authenticated:
            return Response({
                'status':'Information not available',
            }, status=status.HTTP_400_BAD_REQUEST)
        projects = request.user.user_iot_projects
        # Add validation on token authorization per project
        try:
            serialized_projects = serializers.NestedProjectsSerializer(projects, many=True)
            return Response({
                'status':'Information shown',
                'projects':serialized_projects.data, 
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status':'Something went wrong',
                'exception':e,
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"], permission_classes=(permissions.IsAuthenticated,IoTPermissions.IsProjectOwner,))
    def project(self, request, pk=None):
        """
        ## Obtain project information
        ====

        #### Projects can't be created within the API they most be created from within the
        admin console.

        #### Allowed methods:
        * #### *GET*: View details of project
        """
        if not request.user.is_authenticated:
            return Response({
                'status':'Information not available',
            }, status=status.HTTP_400_BAD_REQUEST)
        # Validate url id and ownership of project
        project = get_object_or_404(models.Projects, pk=pk)
        self.check_object_permissions(request, project)
        try:
            serialized_projects = serializers.NestedProjectsSerializer(project, many=False)
            return Response({
                'status':'Information shown',
                'project_{}'.format(pk):serialized_projects.data, 
            }, status=status.HTTP_200_OK)
        except:
            return Response({
                'status':'Something went wrong',
            }, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=True, methods=["get", "post", "delete"], permission_classes=(permissions.IsAuthenticated,IoTPermissions.IsProjectOwner))
    def project_zones(self, request, pk=None):
        """
        ## Manage project zones
        ====

        #### Allowed methods:
        * #### *GET*: Retrives all zones of project
        *Zones found will be returned in the project_zones argument
        within the body*

        * #### *POST*: Allows to add new zones to project
        * #### *DELETE*: Allows to delete project zones

        *In order to create or delete zones you must send the information within request body
        in the argument "zones"*
        ##### Example:
        **DELETE**:
        {
            zones: [
                {
                    id_zone:#1
                },
                {
                    id_zone:#2
                }
            ]
        }
        
        **POST**:
        {
            zones: [
                {
                    name:"",
                    description:""
                }
            ]
        }
        
        ### Notes:
        * The url pk is used as the zone's project ID thus zones created will be linked
        to the matching project
        * *By default the token used on authentication will be registered to control
        the newly created zone*
        """
        ex = 'Unknown'
        msg = ''
        if not request.user.is_authenticated:
            return Response({
                'status':'Information not available',
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Manage incoming post requests project_zones
            if request.method == "POST":
                project = get_object_or_404(models.Projects, pk=pk)
                self.check_object_permissions(request, project)
                zones = request.data['zones']
                ser = serializers.ZonesSerializer(
                    data=zones,
                    many=True,
                    context={
                        'token':request.auth,
                        'project':project
                    }
                )
                if ser.is_valid():
                    ser.save()
                    return Response({
                        'status':'Created zone{}'.format('s' if len(zones)>1 else ''),
                        'zones':ser.data
                    }, status=status.HTTP_201_CREATED)
                else:
                    return Response({
                        'status':'Error while creating zone{}'.format('s' if len(zones) > 1 else ''),
                        'errors':ser.errors,
                    }, status=status.HTTP_400_BAD_REQUEST)

            # Manage incoming delete requests
            elif request.method == "DELETE":
                deleted_zones = []
                for zone in request.data['zones']:
                    z = get_object_or_404(models.Zones,pk=zone['id_zone'])
                    z.delete()
                    deleted_zones.append({'id_zone':zone['id_zone']})
                return Response({
                    'status':'Zone{} deletion succesfull'.format('s' if len(deleted_zones) > 1 else ''),
                    'deleted_zones':deleted_zones
                },status=status.HTTP_200_OK)

            # Manage incoming get requests
            elif request.method == "GET":
                # Validate url id and ownership of project
                project = get_object_or_404(models.Projects,pk=pk)
                self.check_object_permissions(request, project)
                project_zones = project.project_zones
                ser = serializers.ZonesSerializer(project_zones, many=True)
                return Response({
                    'status':'Search successful',
                    'project_zones':ser.data
                })
        except KeyError as e:
            ex = 'KeyError'
            msg = 'If your request is POST or DELETE verify you are sending the zones you want to either create or delete'
        except Exception as e:
            ex = str(e)
            msg = ''
        return Response({
            'status':'Something went wrong',
            'exception':ex,
            'message':msg,
            'pk':pk
        }, status=status.HTTP_400_BAD_REQUEST)


    """
    ============
    Zone
    ============
    """

    @action(detail=True, methods=["get","put","delete"], permission_classes=(permissions.IsAuthenticated,IoTPermissions.IsZoneOwner,))
    def zone(self, request, pk=None):
        """
        ## Manages a specific zone
        ====

        #### Zones might be created, edited, and deleted by zone owners

        #### Allowed methods:
        * #### *GET*: View zone information
        * #### *PUT*: Edit zone basic information
        * #### *DELETE*: Delete the zone

        *If you have have control over the current zone by using the DELETE 
        method you automatically delete it **BE CAREFUL** !*

        *In order to update a zone's information you should send it within request
        body in the argument "zone"*
        ##### Example:
        
        **PUT**:
        {
            zone:{
                name:"",
                description:""
            }
        }
        """
        if not request.user.is_authenticated:
            return Response({
                'status':'Information not available',
            }, status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'PUT':
            zone_data = request.data['zone']
            zone = get_object_or_404(models.Zones,pk=pk)
            ser = serializers.ZonesSerializer(zone, data=zone_data, many=False, partial=True)
            if ser.is_valid():
                ser.save()
                return Response({
                    'status':'Zone updated correctly',
                    'zone_info':ser.data,
                },status=status.HTTP_200_OK)
            else:
                return Response({
                    'status':'Error while updating',
                    'errors':ser.errors,
                },status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            filtered_zone = get_object_or_404(models.Zones,pk=pk)
            self.check_object_permissions(request, filtered_zone)
            filtered_zone.delete()
            return Response({
                'status':'Zone deletion successful'
            }, status=status.HTTP_200_OK)

        elif request.method == 'GET':
            filtered_zone = get_object_or_404(models.Zones,pk=pk)
            self.check_object_permissions(request, filtered_zone)
            ser = serializers.ZonesSerializer(filtered_zone, many=False)
            return Response({
                'status':'Search successful',
                'zone':ser.data
            })

        return Response({
            'status':'Something went wrong',
        }, status=status.HTTP_400_BAD_REQUEST)
    

    @action(detail=True, methods=["get","post","delete"], permission_classes=(permissions.IsAuthenticated,IoTPermissions.IsZoneOwner))
    def zone_nodes(self, request, pk=None):
        """
        ## Manage zone nodes
        ====

        #### Allowed methods:
        * #### *GET*: Retrives all nodes of zone
        *Nodes found will be returned in the zone_nodes argument
        within the body*

        * #### *POST*: Allows to add new nodes to zone
        * #### *DELETE*: Allows to delete zone nodes

        *In order to create or delete nodes you must send the information within request body
        in the argument "nodes"*
        ##### Example:
        **DELETE**:
        {
            nodes: [
                {
                    id_node:#1
                },
                {
                    id_node:#2
                }
            ]
        }
        
        **POST**:
        {
            nodes: [
                {
                    name:"",
                    description:"",
                }
            ]
        }
        
        ### Notes:
        * The url pk is used as the node's zone ID thus nodes created will be linked
        to the matching zone
        * *By default the token used on authentication will be registered to control
        the newly created node*
        """
        ex = 'Unknown'
        msg = ''
        if not request.user.is_authenticated:
            return Response({
                'status':'Information not available',
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Manage incoming post requests
            if request.method == "POST":
                zone = get_object_or_404(models.Zones,pk=pk)
                self.check_object_permissions(request,zone)
                nodes = request.data['nodes']
                ser = serializers.NodeSerializer(
                    data=nodes,
                    many=True,
                    context={
                        'token':request.auth,
                        'zone':zone
                    }
                )
                if ser.is_valid():
                    ser.save()
                    return Response({
                        'status':'Created node{}'.format('s' if len(nodes)>1 else ''),
                        'nodes':ser.data
                    }, status=status.HTTP_201_CREATED)
                else:
                    return Response({
                        'status':'Error while creating node{}'.format('s' if len(sensors)>1 else ''),
                        'errors':ser.errors,
                    }, status=status.HTTP_400_BAD_REQUEST)
            # Manage incoming delete requests
            elif request.method == "DELETE":
                deleted_nodes = []
                for node in request.data['nodes']:
                    n = get_object_or_404(models.Node,pk=node['id_node'])
                    self.check_object_permissions(request, n)
                    n.delete()
                    deleted_nodes.append({'id_node':node['id_node']})
                return Response({
                    'status':'Node{} deletion succesfull'.format('s' if len(deleted_nodes)>1 else ''),
                    'deleted_nodes':deleted_nodes
                }, status=status.HTTP_200_OK)
            # Manage incoming get requests
            elif request.method == "GET":
                zone = get_object_or_404(models.Zones,pk=pk)
                self.check_object_permissions(request, zone)
                zone_nodes = zone.zone_nodes
                ser = serializers.NodeSerializer(zone_nodes, many=True)
                return Response({
                    'status':'Search successful',
                    'zone_nodes':ser.data
                }, status=status.HTTP_200_OK)
        except KeyError as e:
            ex = 'KeyError'
            msg = 'If your request is POST or DELETE verify you are sending the nodes you want to either create or delete'
        except Exception as e:
            ex = str(e)
            msg = ''
        return Response({
            'status':'Something went wrong',
            'exception':ex,
            'message':msg
        }, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=True, methods=["get","post","delete"], permission_classes=(permissions.IsAuthenticated,IoTPermissions.IsZoneOwner))
    def zone_sensors(self, request, pk=None):
        """
        ## Manage zone ambiental sensors
        ====

        #### Allowed methods:
        * #### *GET*: Retrives all sensors of zone
        *Sensors found will be returned in the zone_ambiental_sensors argument
        within the body, remember that in order to access non ambiental sensors
        you must access them through their parent nodes*

        * #### *POST*: Allows to add new ambiental sensors to zone
        * #### *DELETE*: Allows to delete zone ambiental sensors

        *In order to create or delete sensors you must send the information within request body
        in the argument "sensors"*
        ##### Example:
        **DELETE**:
        {
            sensors: [
                {
                    id_sensor:#1
                },
                {
                    id_sensor:#2
                }
            ]
        }
        
        **POST**:
        {
            sensors: [
                {
                    sensor_type:"",
                }
            ]
        }
        
        ### Notes:
        * The url pk is used as the sensors's zone ID thus sensors created will be linked
        to the matching zone
        * By default sensors created via a zone are considered ambiental
        * *Sensor do not have acces keys, they are managed by the zone or node they
        belong to*
        """
        ex = 'Unknown'
        msg = ''
        if not request.user.is_authenticated:
            return Response({
                'status':'Information not available',
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Manage incoming post requests zone_sensors
            if request.method == "POST":
                zone = get_object_or_404(models.Zones,pk=pk)
                self.check_object_permissions(request, zone)
                sensors = request.data['sensors']
                for sensor in sensors:
                    sensor['ambiental'] = True
                ser = serializers.SensorsSerializer(
                    data=sensors,
                    many=True,
                    context={
                        'token':request.auth,
                        'zone':zone
                    }
                )
                if ser.is_valid():
                    ser.save()
                    return Response({
                        'status':'Created sensor{}'.format('s' if len(sensors)>1 else ''),
                        'sensors':ser.data
                    }, status=status.HTTP_201_CREATED)
                else:
                    return Response({
                        'status':'Error while creating sensor{}'.format('s' if len(sensors)>1 else ''),
                        'errors':ser.errors,
                    }, status=status.HTTP_400_BAD_REQUEST)
            # Manage incoming delete requests
            elif request.method == "DELETE":
                deletd_sensors = []
                for sensor in request.data['sensors']:
                    s = get_object_or_404(models.Sensors,pk=sensor['id_sensor'])
                    self.check_object_permissions(request, s)
                    s.delete()
                    deletd_sensors.append({'id_sensor':sensor['id_sensor']})
                return Response({
                    'status':'Sensor{} deletion succesfull'.format('s' if len(deletd_sensors)>1 else ''),
                    'deleted_sensors':deletd_sensors
                },status=status.HTTP_200_OK)
            # Manage incoming get requests
            elif request.method == "GET":
                zone = get_object_or_404(models.Zones,pk=pk)
                self.check_object_permissions(request, zone)
                zone_ambiental_sensors = zone.zone_ambiental_sensors
                ser = serializers.SensorsSerializer(zone_ambiental_sensors, many=True)
                return Response({
                    'status':'Search successful',
                    'zone_ambiental_sensors':ser.data
                }, status=status.HTTP_200_OK)
        except KeyError as e:
            ex = 'KeyError'
            msg = 'If your request is POST or DELETE verify you are sending the sensors you want to either create or delete'
        except Exception as e:
            ex = str(e)
            msg = ''
        return Response({
            'status':'Something went wrong',
            'exception':ex,
            'message':msg
        }, status=status.HTTP_400_BAD_REQUEST)

    """
    ============
    Nodes
    ============
    """

    @action(detail=True, methods=["get","put","delete"], permission_classes=(permissions.IsAuthenticated,IoTPermissions.IsNodeOwner,))
    def node(self, request, pk=None):
        """
        ## Manage a specific node
        ====

        #### Nodes might be created, edited and deleted by node owners

        #### Allowed methods:
        * #### *GET*: View node information
        * #### *PUT*: Edit node basic information
        * #### *DELETE*: Delete the node

        *If you have have control over the current node by using the DELETE 
        method you automatically delete it **BE CAREFUL** !*

        *In order to update a node's information you should send it within request
        body in the argument "node"*
        ##### Example:
        
        **PUT**:
        {
            zone:{
                name:"",
                description:""
            }
        }
        """
        if request.method == 'PUT':
            pass
        elif request.method == 'GET':
            filtered_node = get_object_or_404(models.Node,pk=pk)
            self.check_object_permissions(request, filtered_node)
            ser = serializers.NodeSerializer(filtered_node, many=True)
            return Response({
                'status':'Search successful',
                'nodes':ser.data
            }, status=status.HTTP_200_OK)
        return Response({
            'status':'Information shown',
        }, status=status.HTTP_200_OK)


    @action(detail=True, methods=['get','post','put'], permission_classes=(permissions.IsAuthenticated,IoTPermissions.IsNodeOwner,))
    def node_sensors(self, request, pk=None):
        """
        ## Manage node sensors
        ====

        #### Allowed methods:
        * #### *GET*: Retrives all sensors of node
        *Sensors found will be returned in the node_sensors argument
        within the body*

        * #### *POST*: Allows to add new sensors to node
        * #### *DELETE*: Allows to delete node sensors

        *In order to create or delete sensors you must send the information within request body
        in the argument "sensors"*
        ##### Example:
        **DELETE**:
        {
            sensors: [
                {
                    id_sensor:#1
                },
                {
                    id_sensor:#2
                }
            ]
        }
        
        **POST**:
        {
            sensors: [
                {
                    sensor_type:"",
                }
            ]
        }
        
        ### Notes:
        * The url pk is used as the sensors's zone ID thus sensors created will be linked
        to the matching zone
        * By default sensors created via a node are not considered as ambiental
        * *Sensor do not have acces keys, they are managed by the zone or node they
        belong to*
        """
        ex = 'Unknown'
        msg = ''
        if not request.user.is_authenticated:
            return Response({
                'status':'Information not available',
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Manage incoming post requests zone_sensors
            if request.method == "POST":
                node = get_object_or_404(models.Node,pk=pk)
                self.check_object_permissions(request, node)
                sensors = request.data['sensors']
                ser = serializers.SensorsSerializer(
                    data=sensors,
                    many=True,
                    context={
                        'token':request.auth,
                        'zone':node.zone,
                        'node':node
                    }
                )
                if ser.is_valid():
                    ser.save()
                    return Response({
                        'status':'Created sensor{}'.format('s' if len(sensors)>1 else ''),
                        'sensors':ser.data
                    }, status=status.HTTP_201_CREATED)
                else:
                    return Response({
                        'status':'Error while creating sensor{}'.format('s' if len(sensors)>1 else ''),
                        'errors':ser.errors,
                    }, status=status.HTTP_400_BAD_REQUEST)
            # Manage incoming delete requests
            elif request.method == "DELETE":
                deletd_sensors = []
                for sensor in request.data['sensors']:
                    s = get_object_or_404(models.Sensors,pk=sensor['id_sensor'])
                    self.check_object_permissions(request, s)
                    s.delete()
                    deletd_sensors.append({'id_sensor':sensor['id_sensor']})
                return Response({
                    'status':'Sensor{} deletion succesfull'.format('s' if len(deletd_sensors)>1 else ''),
                    'deleted_sensors':deletd_sensors
                },status=status.HTTP_200_OK)
            # Manage incoming get requests
            elif request.method == "GET":
                node = get_object_or_404(models.Node,pk=pk)
                self.check_object_permissions(request, node)
                node_sensors = zone.node_sensors
                ser = serializers.SensorsSerializer(node_sensors, many=True)
                return Response({
                    'status':'Search successful',
                    'node_sensors':ser.data
                }, status=status.HTTP_200_OK)
        except KeyError as e:
            ex = 'KeyError'
            msg = 'If your request is POST or DELETE verify you are sending the sensors you want to either create or delete'
        except Exception as e:
            ex = str(e)
            msg = ''
        return Response({
            'status':'Something went wrong',
            'exception':ex,
            'message':msg
        }, status=status.HTTP_400_BAD_REQUEST)
    """
    ============
    Measurements
    ============
    """    

    @action(detail=False, methods=["post",], permission_classes=(permissions.IsAuthenticated,IoTPermissions.CanManageSensor,))
    def measure(self, request):
        ex = 'Unknown'
        msg = ''
        try:
            measurements =  request.data['sensors']
            for m in measurements:
                self.check_object_permissions(request, get_object_or_404(models.Sensors,pk=m['id_sensor']))

            s_serializer = serializers.MeasurementSerializer(data=measurements, many=True)
            if s_serializer.is_valid():
                s_serializer.save()
                return Response({
                    'status':'Information shown',
                    'received':s_serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'status':'Error on data',
                    'errors':json.dumps(s_serializer.errors),
                }, status=status.HTTP_400_BAD_REQUEST)
        
        except KeyError as e:
            ex = 'KeyError'
            msg = 'Verify you are sending the measurements you want to create inside the "sensors" parameter within the body'
        except Exception as e:
            ex = str(e)
            msg = ''
        return Response({
            'status':'Something went wrong',
            'exception':ex,
            'message':msg
        }, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=True, methods=["get",], permission_classes=(permissions.IsAuthenticated,IoTPermissions.CanManageSensor,))
    def sensor_measurements(self, request, pk=None):
        try:
            sensor = get_object_or_404(models.Sensors,pk=pk)
            self.check_object_permissions(request, sensor)
            ser = serializers.NestedSensorSerializer(sensor, many=False)
            return Response({
                'status':'Sensor found',
                'sensor':ser.data,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status':'No sensor matching id {}'.format(pk),
            }, status=status.HTTP_400_BAD_REQUEST)