from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from users.models import GeneralUser, CustomAccessTokens
from IoT.api.views import IoTProjectsViewSet
import IoT.models as models
import IoT.model_choices as choices

class ZoneManagementTestCase(TestCase):
    """
    Test Zone management from Project via Api
    """
    client_api = APIClient()
    user = None
    project_token = ""
    project_id = None
    zone_id = None

    def CreateZone(self):
        """
        Create zone for testing

        No token assigned

        Returns:
            model Zone instance
        """
        # Validate requirements
        self.assertNotEqual(self.user, None)
        # Create project
        project = models.Projects.objects.create(
            user=self.user,
            name='Test',
            description='Test project',
            snippet_title='Test Snippet',
            snippet_image='image.png',
        )
        # Create zone
        zone = models.Zones.objects.create(
            name="Updated name zone 1",
            description="New updated zone 1 description",
            project=project,
        )
        return zone


    def CreateNodes(self,z,n=2):
        """
        Create n nodes for zone z

        No token assigned

        Returns:
            [node model instace]
        """
        # Validate requirements
        self.assertNotEqual(self.user,None)
        self.assertNotEqual(z, None)
        # Create zone
        nodes = []
        for node in range(n):
            # Create node
            nodes.append(
                models.Node.objects.create(
                    zone=z,
                    name="Test node UA{}".format(node),
                    description="Test node for management {}".format(node)
                )
            )
        return nodes


    def CreateSensors(self,z,n=2):
        """
        Create n sensors for zone z

        No token assigned

        Returns:
            [sensor model instace]
        """
        # Validate requirements
        self.assertNotEqual(self.user,None)
        self.assertNotEqual(z, None)
        # Create zone
        sensors = []
        for s in range(n):
            # Create node
            sensors.append(
                models.Sensors.objects.create(
                    zone=z,
                    sensor_type=choices.DHT22,
                    ambiental=True
                )
            )
        return sensors


    def setUp(self):
        # Create User
        user = GeneralUser.objects.create_user(
            username = 'TestUser',
            password = "123Password",
            email = 'test@test.com'
        )
        self.user = user
        # Create and save project token
        token = CustomAccessTokens(
            user=user,
            name="testToken"
        )
        self.project_token = token.uuid_token
        token.save()
        # Create project
        project = models.Projects.objects.create(
            user=user,
            name='Test',
            description='Test project',
            snippet_title='Test Snippet',
            snippet_image='image.png',
        )
        project.access_keys.add(token)
        self.project_id = project.id


    def test_api_create_delete_zone(self):
        """
        Attempt creating and deleting a zone via the rest api via 
        project it belongs to
        """
        # Validate we have project id
        self.assertNotEqual(self.project_id, None)
        # Count number of zones
        number_zones = len(models.Zones.objects.all())
        # Create url
        url_project_zones = reverse('iot_api:iot_general_api-project-zones', args=(self.project_id,))
        # Create headers
        header = {'HTTP_CA_TOKEN': self.project_token}
        # Post data
        zone_data = {
            "zones":[
                {
                    "name":"Test Zone 1",
                    "description":"First test zone created from api"
                }
            ]
        }
        post_response = self.client_api.post(
            url_project_zones,
            zone_data,
            format='json',
            **header
            )
        self.assertEqual(post_response.status_code, 201) # New Zone created
        zone_id = post_response.data['zones'][0]['id'] # Save newly created id
        # Delete zone
        zones_to_delete = {
            "zones":[
                {
                    "id_zone":zone_id
                }
            ]
        }
        delete_response = self.client_api.delete(
            url_project_zones,
            zones_to_delete,
            format='json',
            **header
        )
        self.assertEqual(delete_response.status_code, 200) # Zone deleted
        self.assertEqual(delete_response.data['deleted_zones'], [{"id_zone":zone_id}])
        self.assertEqual(number_zones, len(models.Zones.objects.all()))


    def test_create_edit_delete_zone(self):
        """
        Test creating a zone, editing it and deleting it via itself
        """
        # Validate we have project id
        self.assertNotEqual(self.project_id, None)
        # Count number of zones
        number_zones = len(models.Zones.objects.all())
        # Create url
        url_project_zones = reverse('iot_api:iot_general_api-project-zones', args=(self.project_id,))
        # Create headers
        header = {'HTTP_CA_TOKEN': self.project_token}
        # Post data
        zone_data = {
            "zones":[
                {
                    "name":"Test Zone 1",
                    "description":"First test zone created from api"
                }
            ]
        }
        post_response = self.client_api.post(
            url_project_zones,
            zone_data,
            format='json',
            **header
            )
        self.assertEqual(post_response.status_code, 201) # New Zone created
        zone_id = post_response.data['zones'][0]['id'] # Save newly created id
        # Create zone url
        url_zones = reverse('iot_api:iot_general_api-zone', args=(zone_id,))
        zone_put_data = {
            "zone":{
                "name":"Updated name zone 1",
                "description":"New updated zone 1 description"
            }
        }
        put_response = self.client_api.put(
            url_zones,
            zone_put_data,
            format='json',
            **header
        )
        self.assertEqual(models.Zones.objects.get(pk=zone_id).name, "Updated name zone 1")
        self.assertEqual(put_response.status_code, 200) # Updated correctly
        delete_response = self.client_api.delete(
            url_zones,
            format='json',
            **header
        )
        self.assertEqual(delete_response.status_code, 200) # Zone deletion successful
        self.assertEqual(number_zones, len(models.Zones.objects.all()))


    def test_create_get_delete_zone(self):
        """
        Create a zone, get it and delete it
        """
        # Validate we have project id
        self.assertNotEqual(self.project_id, None)
        # Count number of zones
        number_zones = len(models.Zones.objects.all())
        # Create url
        url_project_zones = reverse('iot_api:iot_general_api-project-zones', args=(self.project_id,))
        # Create headers
        header = {'HTTP_CA_TOKEN': self.project_token}
        # Post data
        zone_data = {
            "zones":[
                {
                    "name":"Test Zone 1",
                    "description":"First test zone created from api"
                }
            ]
        }
        post_response = self.client_api.post(
            url_project_zones,
            zone_data,
            format='json',
            **header
            )
        self.assertEqual(post_response.status_code, 201) # New Zone created
        zone_id = post_response.data['zones'][0]['id'] # Save newly created id
        created_zone = post_response.data['zones'][0]
        # Get zone
        url_zone = reverse('iot_api:iot_general_api-zone', args=(zone_id,))
        get_response = self.client_api.get(
            url_zone,
            format='json',
            **header
        )
        self.assertEqual(get_response.status_code, 200) # Information retrived
        self.assertEqual(get_response.data['zone'], created_zone)
        # Delete zone
        delete_response = self.client_api.delete(
            url_zone,
            format='json',
            **header
        )
        self.assertEqual(delete_response.status_code, 200) # Zone deleted
        self.assertEqual(number_zones, len(models.Zones.objects.all()))


    def test_create_delete_node(self):
        # Create User
        user = GeneralUser.objects.create_user(
            username = 'TestUser2',
            password = "123Password2",
            email = 'test2@test.com'
        )
        # Create and save project token
        token = CustomAccessTokens(
            user=user,
            name="testToken"
        )
        project_token = token.uuid_token
        token.save()
        # Create project
        project = models.Projects.objects.create(
            user=user,
            name='Test',
            description='Test project',
            snippet_title='Test Snippet',
            snippet_image='image.png',
        )
        # Create zone
        zone = models.Zones.objects.create(
            name="Updated name zone 1",
            description="New updated zone 1 description",
            project=project,
        )
        zone.access_keys.add(token)
        zone.save()
        # Create url
        url_zone_nodes = reverse('iot_api:iot_general_api-zone-nodes', args=(zone.id,))
        # Create headers
        header = {'HTTP_CA_TOKEN': project_token}
        # Count existing nodes
        number_nodes = len(models.Node.objects.all())
        # Create node
        node_data = {
            'nodes':[
                {
                    "name":"Test Node",
                    "description":"A newly created node"
                }
            ]
        }
        post_response = self.client_api.post(
            url_zone_nodes,
            node_data,
            format='json',
            **header
        )
        self.assertEqual(post_response.status_code, 201) # New node created
        node_id = post_response.data['nodes'][0]['id']
        delete_list = {
            "nodes":[
                {
                    "id_node":node_id,
                }
            ]
        }
        delete_response = self.client_api.delete(
            url_zone_nodes,
            delete_list,
            format='json',
            **header
        )
        self.assertEqual(delete_response.status_code, 200) # Node deleted
        self.assertEqual(number_nodes, len(models.Node.objects.all()))
        user.delete()


    def test_create_delete_sensor(self):
        # Create User
        user = GeneralUser.objects.create_user(
            username = 'TestUser2',
            password = "123Password2",
            email = 'test2@test.com'
        )
        # Create and save project token
        token = CustomAccessTokens(
            user=user,
            name="testToken"
        )
        project_token = token.uuid_token
        token.save()
        # Create project
        project = models.Projects.objects.create(
            user=user,
            name='Test',
            description='Test project',
            snippet_title='Test Snippet',
            snippet_image='image.png',
        )
        # Create zone
        zone = models.Zones.objects.create(
            name="Updated name zone 1",
            description="New updated zone 1 description",
            project=project,
        )
        zone.access_keys.add(token)
        zone.save()
        # Create url
        url_zone_sensors = reverse('iot_api:iot_general_api-zone-sensors', args=(zone.id,))
        # Create headers
        header = {'HTTP_CA_TOKEN': project_token}
        # Count existing nodes
        number_sensors = len(models.Sensors.objects.all())
        # Create node
        sensors_data = {
            'sensors':[
                {
                    "sensor_type":choices.DHT22,
                },
                {
                    "sensor_type":choices.DHT11,
                }
            ]
        }
        post_response = self.client_api.post(
            url_zone_sensors,
            sensors_data,
            format='json',
            **header
        )
        self.assertEqual(post_response.status_code, 201) # New sensors created
        self.assertEqual(len(models.Sensors.objects.all()), number_sensors + 2)
        # Get sensor ids
        f_sensor_id = post_response.data['sensors'][0]['id']
        s_sensor_id = post_response.data['sensors'][1]['id']
        # Validate created sensors are ambiental
        f_sensor = models.Sensors.objects.get(pk=f_sensor_id)
        self.assertEqual(f_sensor.ambiental, True)
        s_sensor = models.Sensors.objects.get(pk=s_sensor_id)
        self.assertEqual(s_sensor.ambiental, True)
        # Delete sensors
        delete_list = {
            "sensors":[
                {
                    "id_sensor":f_sensor_id,
                },
                {
                    "id_sensor":s_sensor_id,
                },
            ]
        }
        delete_response = self.client_api.delete(
            url_zone_sensors,
            delete_list,
            format='json',
            **header
        )
        self.assertEqual(delete_response.status_code, 200) # Node deleted
        self.assertEqual(len(models.Sensors.objects.all()), number_sensors)
        # Delete second sensor
        user.delete()


    def test_unauthorized_zone(self):
        """
        Test unauthorized zone information modification, 
        aquisition and deletion
        """
        self.assertNotEqual(self.project_token, None)
        # Create zone
        zone = self.CreateZone()
        # Count total zones
        count_zones = len(models.Zones.objects.all())
        # Create zone url
        zone_url = reverse('iot_api:iot_general_api-zone', args=(zone.id,))
        # Create wrong token
        header = {'HTTP_CA_TOKEN':self.project_token}
        # Test no header get
        get_nh_response = self.client_api.get(
            zone_url,
            format="json"
        )
        self.assertEqual(zone, models.Zones.objects.get(id=zone.id))
        self.assertTrue(
            get_nh_response.status_code == 403 or 
            get_nh_response.status_code == 401 or 
            get_nh_response.status_code == 400
        )
        self.assertEqual(count_zones, len(models.Zones.objects.all()))
        # Test get wrong token
        get_response = self.client_api.get(
            zone_url,
            format="json",
            **header
        )
        self.assertEqual(zone, models.Zones.objects.get(id=zone.id))
        self.assertTrue(
            get_response.status_code == 403 or 
            get_response.status_code == 401 or 
            get_response.status_code == 400
        )
        self.assertEqual(count_zones, len(models.Zones.objects.all()))
        # Test put no header
        zone_put_data = {
            "zone":{
                "name":"Updated name zone 1",
                "description":"New updated zone 1 description"
            }
        }
        put_nh_response = self.client_api.put(
            zone_url,
            zone_put_data,
            format="json",
        )
        self.assertEqual(zone, models.Zones.objects.get(id=zone.id))
        self.assertTrue(
            put_nh_response.status_code == 403 or 
            put_nh_response.status_code == 401 or 
            put_nh_response.status_code == 400
        )
        self.assertEqual(count_zones, len(models.Zones.objects.all()))
        # Test put wrong header
        put_response = self.client_api.put(
            zone_url,
            zone_put_data,
            format="json",
            **header
        )
        self.assertEqual(zone, models.Zones.objects.get(id=zone.id))
        self.assertTrue(
            put_response.status_code == 403 or 
            put_response.status_code == 401 or 
            put_response.status_code == 400
        )
        self.assertEqual(count_zones, len(models.Zones.objects.all()))
        # Test delete no header
        delete_nh_response = self.client_api.delete(
            zone_url,
            format="json",
        )
        self.assertEqual(zone, models.Zones.objects.get(id=zone.id))
        self.assertTrue(
            delete_nh_response.status_code == 403 or 
            delete_nh_response.status_code == 401 or 
            delete_nh_response.status_code == 400
        )
        self.assertEqual(count_zones, len(models.Zones.objects.all()))
        # Test delete wrong header
        delete_response = self.client_api.delete(
            zone_url,
            format="json",
            **header
        )
        self.assertEqual(zone, models.Zones.objects.get(id=zone.id))
        self.assertTrue(
            delete_response.status_code == 403 or 
            delete_response.status_code == 401 or 
            delete_response.status_code == 400
        )
        self.assertEqual(count_zones, len(models.Zones.objects.all()))


    def test_unauthorized_zone_nodes(self):
        """
        Test unauthorized request to zone nodes aquisition, creation and deletion
        """
        self.assertNotEqual(self.project_token, None)
        # Create zone
        zone = self.CreateZone()
        nodes = self.CreateNodes(zone,2)
        # Count nodes
        node_count = len(models.Node.objects.all())
        # Create node zones url
        url_zone_nodes = reverse('iot_api:iot_general_api-zone-nodes', args=(zone.id,))
        # Create header
        header = {'HTTP_CA_TOKEN':self.project_token}
        # Attempt to get no header
        get_nh_response = self.client_api.get(
            url_zone_nodes,
            format="json"
        )
        self.assertEqual(zone.zone_nodes, models.Zones.objects.get(id=zone.id).zone_nodes)
        self.assertTrue(
            get_nh_response.status_code == 403 or 
            get_nh_response.status_code == 401 or 
            get_nh_response.status_code == 400
        )
        self.assertEqual(len(models.Node.objects.all()), node_count)
        # Attempt to get wrong token
        get_response = self.client_api.get(
            url_zone_nodes,
            format="json",
            **header
        )
        self.assertEqual(zone.zone_nodes, models.Zones.objects.get(id=zone.id).zone_nodes)
        self.assertTrue(
            get_response.status_code == 403 or 
            get_response.status_code == 401 or 
            get_response.status_code == 400
        )
        self.assertEqual(len(models.Node.objects.all()), node_count)
        # Attempt to create nodes
        node_data = {
            'nodes':[
                {
                    "name":"Test Node",
                    "description":"A newly created node"
                }
            ]
        }
        # Attempt to post no header
        post_nh_response = self.client_api.post(
            url_zone_nodes,
            node_data,
            format="json"
        )
        self.assertEqual(zone.zone_nodes, models.Zones.objects.get(id=zone.id).zone_nodes)
        self.assertTrue(
            post_nh_response.status_code == 403 or 
            post_nh_response.status_code == 401 or 
            post_nh_response.status_code == 400
        )
        self.assertEqual(len(models.Node.objects.all()), node_count)
        # Attempt to post wrong token
        post_response = self.client_api.post(
            url_zone_nodes,
            node_data,
            format="json",
            **header
        )
        self.assertEqual(zone.zone_nodes, models.Zones.objects.get(id=zone.id).zone_nodes)
        self.assertTrue(
            post_response.status_code == 403 or 
            post_response.status_code == 401 or 
            post_response.status_code == 400
        )
        self.assertEqual(len(models.Node.objects.all()), node_count)
        # Attempt delete
        node_delete_list = {
            "nodes":[{'id_node':n.id} for n in nodes]
        }
        # Count nodes
        node_count = len(models.Node.objects.all())
        # No headers
        delete_nh_response = self.client_api.delete(
            url_zone_nodes,
            node_delete_list,
            format="json"
        )
        self.assertEqual(zone.zone_nodes, models.Zones.objects.get(id=zone.id).zone_nodes)
        self.assertTrue(
            delete_nh_response.status_code == 403 or 
            delete_nh_response.status_code == 401 or 
            delete_nh_response.status_code == 400
        )
        self.assertEqual(len(models.Node.objects.all()), node_count)
        # Wrong token
        delete_response = self.client_api.delete(
            url_zone_nodes,
            node_delete_list,
            format="json",
            **header
        )
        self.assertEqual(zone.zone_nodes, models.Zones.objects.get(id=zone.id).zone_nodes)
        self.assertTrue(
            delete_response.status_code == 403 or 
            delete_response.status_code == 401 or 
            delete_response.status_code == 400
        )
        self.assertEqual(len(models.Node.objects.all()), node_count)

        
    def test_unauthorized_zone_sensors(self):
        """
        Test unauthorized zone sensors aquisition, deletion and creation
        """
        self.assertNotEqual(self.project_token, None)
        # Create zone
        zone = self.CreateZone()
        sensors = self.CreateSensors(zone,2)
        # Count sensors
        sensor_count = len(models.Sensors.objects.all())
        # Create node zones url
        url_zone_sensors = reverse('iot_api:iot_general_api-zone-sensors', args=(zone.id,))
        # Create header
        header = {'HTTP_CA_TOKEN':self.project_token}
        # Attempt to get no header
        get_nh_response = self.client_api.get(
            url_zone_sensors,
            format="json"
        )
        self.assertEqual(zone.zone_ambiental_sensors, models.Zones.objects.get(id=zone.id).zone_ambiental_sensors)
        self.assertTrue(
            get_nh_response.status_code == 403 or 
            get_nh_response.status_code == 401 or 
            get_nh_response.status_code == 400
        )
        self.assertEqual(len(models.Sensors.objects.all()), sensor_count)
        # Attempt to get wrong token
        get_response = self.client_api.get(
            url_zone_sensors,
            format="json",
            **header
        )
        self.assertEqual(zone.zone_ambiental_sensors, models.Zones.objects.get(id=zone.id).zone_ambiental_sensors)
        self.assertTrue(
            get_response.status_code == 403 or 
            get_response.status_code == 401 or 
            get_response.status_code == 400
        )
        self.assertEqual(len(models.Sensors.objects.all()), sensor_count)
        # Attempt to create nodes
        sensor_data = {
            'sensors':[
                {
                    'sensor_type':choices.DHT22
                },
                {
                    'sensor_type':choices.DHT11
                },
                {
                    'sensor_type':choices.LDR
                }
            ]
        }
        # Attempt to post no header
        post_nh_response = self.client_api.post(
            url_zone_sensors,
            sensor_data,
            format="json"
        )
        self.assertEqual(zone.zone_ambiental_sensors, models.Zones.objects.get(id=zone.id).zone_ambiental_sensors)
        self.assertTrue(
            post_nh_response.status_code == 403 or 
            post_nh_response.status_code == 401 or 
            post_nh_response.status_code == 400
        )
        self.assertEqual(len(models.Sensors.objects.all()), sensor_count)
        # Attempt to post wrong token
        post_response = self.client_api.post(
            url_zone_sensors,
            sensor_data,
            format="json",
            **header
        )
        self.assertEqual(zone.zone_ambiental_sensors, models.Zones.objects.get(id=zone.id).zone_ambiental_sensors)
        self.assertTrue(
            post_response.status_code == 403 or 
            post_response.status_code == 401 or 
            post_response.status_code == 400
        )
        self.assertEqual(len(models.Sensors.objects.all()), sensor_count)
        # Attempt delete
        delete_list = {
            'sensors':[{'id_sensor':s.id} for s in sensors]
        }
        # Count nodes
        sensor_count = len(models.Sensors.objects.all())
        # No headers
        delete_nh_response = self.client_api.delete(
            url_zone_sensors,
            delete_list,
            format="json"
        )
        self.assertEqual(zone.zone_ambiental_sensors, models.Zones.objects.get(id=zone.id).zone_ambiental_sensors)
        self.assertTrue(
            delete_nh_response.status_code == 403 or 
            delete_nh_response.status_code == 401 or 
            delete_nh_response.status_code == 400
        )
        self.assertEqual(len(models.Sensors.objects.all()), sensor_count)
        # Wrong token
        delete_response = self.client_api.delete(
            url_zone_sensors,
            delete_list,
            format="json",
            **header
        )
        self.assertEqual(zone.zone_ambiental_sensors, models.Zones.objects.get(id=zone.id).zone_ambiental_sensors)
        self.assertTrue(
            delete_response.status_code == 403 or 
            delete_response.status_code == 401 or 
            delete_response.status_code == 400
        )
        self.assertEqual(len(models.Sensors.objects.all()), sensor_count)