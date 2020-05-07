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
