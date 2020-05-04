from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from rest_framework.authentication import  BasicAuthentication
from users.api.cauth import CAccessTokenRestAuth
from users.models import GeneralUser
import IoT.api.serializers as serializers
import IoT.models as models
import IoT.api.permissions as IoTPermissions
import json

class IoTProjectsViewSet(viewsets.ViewSet):
    """
    General IoT project api conncetions managment.
    """
    authentication_classes = (BasicAuthentication,CAccessTokenRestAuth, )

    @action(detail=True, methods=["get"], permission_classes=(permissions.IsAuthenticated,IoTPermissions.IsProjectOwner,))
    def projects(self, request, pk=None):
        """
        ## Obtain project information
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
        # Validate url id and ownership of project
        project = models.Projects.objects.get(pk=pk)
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


    @action(detail=True, methods=["get", "post", "delete"], permission_classes=(permissions.IsAuthenticated,IoTPermissions.IsProjectOwner,IoTPermissions.IsZoneOwner))
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

        *In order to create or delete zones you should send it within request body
        in the argument "zones"*
        ##### Example:
        *DELETE*:
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
        
        *POST*:
        {
            zones: [
                {
                    name:"",
                    description:"",
                    id_project:#project_pk
                }
            ]
        }
        
        *By default the token used on authentication will be registered to control
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
                zones = request.data['zones']
                ser = serializers.ZonesSerializer(data=zones, many=True, context={'token':request.auth})
                if ser.is_valid():
                    ser.save()
                    return Response({
                        'status':'Created zone{}'.format('s' if len(zones) > 1 else ''),
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
                    z = get_object_or_404(Zones,pk=zone['id_zone'])
                    self.check_object_permissions(request, z)
                    z.delete()
                    deleted_zones.append({'id_zone':zone['id_zone']})
                return Response({
                    'status':'Zone{} deletion succesfull'.format('s' if len(deleted_zones) > 1 else ''),
                    'deleted_zones':deleted_zones
                },status=status.HTTP_200_OK)

            # Manage incoming get requests
            elif request.method == "GET":
                # Validate url id and ownership of project
                project = models.Projects.objects.get(pk=pk)
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
            'message':msg
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get","put"], permission_classes=(permissions.IsAuthenticated,IoTPermissions.IsZoneOwner,))
    def zone(self, request, pk=None):
        """
        ## Manage zones
        ====

        #### Zones might be created and edited by zone owners

        #### Allowed methods:
        * #### *GET*: View zone information
        * #### *PUT*: Edit zone basic information

        *In order to update a zone's information you should send it within request
        body in the argument "zone"*
        ##### Example:
        """
        filtered_zone = models.Zones.objects.get(pk=pk)
        if not request.user.is_authenticated:
            return Response({
                'status':'Information not available',
            }, status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'PUT':
            zone_data = request.data['zone']
            zone = get_object_or_404(Zones,pk=zone_data['id'])
            print(zone)
            ser = serializers.ZonesSerializer(zone, data=zone_data, many=False, partial=True)
            if ser.is_valid():
                ser.save()
                return Response({
                    'status':'Zone updated correctly',
                    'zone_info':ser.data,
                },status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'status':'Error while updating',
                    'errors':ser.errors,
                },status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'GET':
            self.check_object_permissions(request, filtered_zone)
            ser = serializers.ZonesSerializer(filtered_zone, many=False)
            return Response({
                'status':'Search successful',
                'zone':ser.data
            })

        return Response({
            'status':'Something went wrong',
        }, status=status.HTTP_400_BAD_REQUEST)
    

    @action(detail=True, methods=["get","post"], permission_classes=(permissions.IsAuthenticated,IoTPermissions.IsNodeOwner,))
    def node(self, request, pk=None):
        if request.method == 'POST':
            pass
        elif request.method == 'GET':
            filtered_node = models.Node.objects.filter(pk=pk)
            self.check_object_permissions(request, filtered_node)
            ser = serializers.NodeSerializer(filtered_node, many=True)
            return Response({
                'status':'Search successful',
                'nodes':ser.data
            }, status=status.HTTP_200_OK)
        return Response({
            'status':'Information shown',
        }, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=["post",], permission_classes=(permissions.IsAuthenticated,IoTPermissions.CanManageSensor,))
    def measure(self, request):
        print("algo")
        measurements =  request.data['sensors']
        print(measurements)
        for m in measurements:
            self.check_object_permissions(request, models.Sensors.objects.get(pk=m['id_sensor']))

        s_serializer = serializers.MeasurementSerializer(data=measurements, many=True)
        if s_serializer.is_valid():
            s_serializer.save()
            return Response({
                'status':'Information shown',
                'received':s_serializer.data
            }, status=status.HTTP_200_OK)
        else:
            print(s_serializer.errors)
            return Response({
                'status':'Error on data',
                'errors':json.dumps(s_serializer.errors),
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get",], permission_classes=(permissions.IsAuthenticated,IoTPermissions.CanManageSensor,))
    def sensor_measurements(self, request, pk=None):
        try:
            sensor = models.Sensors.objects.get(pk=pk)
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