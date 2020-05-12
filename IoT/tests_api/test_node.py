from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from users.models import GeneralUser, CustomAccessTokens
from IoT.api.views import IoTProjectsViewSet
import IoT.models as models
import IoT.model_choices as choices

class NodeManagementTestCase(TestCase):
    """
    Test Zone management from Project via Api
    """
    client_api = APIClient()
    user = None
    zone_token = ""
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
        self.zone_token = token.uuid_token
        token.save()
        # Create project
        project = models.Projects.objects.create(
            user=user,
            name='Test',
            description='Test project',
            snippet_title='Test Snippet',
            snippet_image='image.png',
        )
        zone = models.Zones.objects.create(
            project=project,
            name='Test zone',
            description='Test zone for node management',
        )
        self.zone_id = zone.id
        zone.access_keys.add(token)
        zone.save()


    def test_create_edit_delete_node(self):
        """
        Create a node edit it and delete it via the api
        """
        self.assertNotEqual(self.zone_token, "")
        self.assertNotEqual(self.zone_id, None)
        # Create zone url 
        url_zone_nodes = reverse('iot_api:iot_general_api-zone-nodes', args=(self.zone_id,))
        # Create header =
        header = {'HTTP_CA_TOKEN':self.zone_token}
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
        # Create node url
        url_node = reverse('iot_api:iot_general_api-node', args=(node_id,))
        # Update node
        node_updated_data = {
            'node':{
                'name':'Test name u'
            }
        }
        put_response = self.client_api.put(
            url_node,
            node_updated_data,
            format='json',
            **header
        )
        self.assertEqual(put_response.status_code, 200) # Node updated correctly
        self.assertEqual(put_response.data['node_info']['name'], "Test name u")
        # Delete node
        delete_response = self.client_api.delete(
            url_node,
            format='json',
            **header
        )
        self.assertEqual(delete_response.status_code, 200) # Node deleted
        self.assertEqual(number_nodes, len(models.Node.objects.all()))
        

    def test_create_get_delete_node(self):
        """
        Create get information and delete node
        """
        self.assertNotEqual(self.zone_token, "")
        self.assertNotEqual(self.zone_id, None)
        # Create zone url 
        url_zone_nodes = reverse('iot_api:iot_general_api-zone-nodes', args=(self.zone_id,))
        # Create header =
        header = {'HTTP_CA_TOKEN':self.zone_token}
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
        created_node = post_response.data['nodes'][0]
        # Create node url
        url_node = reverse('iot_api:iot_general_api-node', args=(node_id,))
        get_response = self.client_api.get(
            url_node,
            format='json',
            **header
        )
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.data['node'], created_node)
        delete_response = self.client_api.delete(
            url_node,
            format='json',
            **header
        )
        self.assertEqual(delete_response.status_code, 200) # Node deleted
        self.assertEqual(number_nodes, len(models.Node.objects.all()))


    def test_create_get_delete_node_sensors(self):
        """
        Test creation of node sensors
        """
        # Create User
        user = GeneralUser.objects.create_user(
            username = 'TestUser2',
            password = "123Password",
            email = 'test2@test.com'
        )
        # Create and save project token
        token = CustomAccessTokens(
            user=user,
            name="testToken"
        )
        node_token = token.uuid_token
        token.save()
        # Create project
        project = models.Projects.objects.create(
            user=user,
            name='Test',
            description='Test project',
            snippet_title='Test Snippet',
            snippet_image='image.png',
        )
        zone = models.Zones.objects.create(
            project=project,
            name='Test zone',
            description='Test zone for node management',
        )
        node = models.Node.objects.create(
            zone=zone,
            name="Test node",
            description="Test node for management"
        )
        node.access_keys.add(token)
        node.save()
        # Create node url
        url_node = reverse('iot_api:iot_general_api-node-sensors', args=(node.id,))
        # Count sensors
        number_sensors = len(models.Sensors.objects.all())
        # Create header =
        header = {'HTTP_CA_TOKEN':node_token}
        # Create sensors
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
        post_response = self.client_api.post(
            url_node,
            sensor_data,
            format='json',
            **header
        )
        self.assertEqual(post_response.status_code, 201) # Sensors created
        sensors = post_response.data['sensors']
        for sensor in sensors:
            self.assertEqual(sensor['ambiental'], False)
        # Get sensors
        get_response = self.client_api.get(
            url_node,
            format='json',
            **header
        )
        self.assertEqual(get_response.status_code, 200) # Sensors retrived
        self.assertEqual(get_response.data['node_sensors'], sensors)
        # Delete sensors
        sensors_ids = [{'id_sensor':i['id']} for i in sensors]
        delete_list = {
            'sensors':sensors_ids
        }
        delete_response = self.client_api.delete(
            url_node,
            delete_list,
            format='json',
            **header
        )
        self.assertEqual(delete_response.status_code, 200) # Sensors deleted
        self.assertEqual(number_sensors, len(models.Sensors.objects.all()))
        user.delete()


    def test_unauthorized_node(self):
        """
        Test accessing node with bad credentials
        """
        # Check needed
        self.assertNotEqual(self.user, None)
        # Create and save token
        token = CustomAccessTokens(
            user=self.user,
            name="testToken"
        )
        node_token = token.uuid_token
        token.save()
        # Create project
        project = models.Projects.objects.create(
            user=self.user,
            name='Test UA',
            description='Test project',
            snippet_title='Test Snippet',
            snippet_image='image.png',
        )
        # Create zone
        zone = models.Zones.objects.create(
            project=project,
            name='Test zone UA',
            description='Test zone for node management',
        )
        # Create node
        node = models.Node.objects.create(
            zone=zone,
            name="Test node UA",
            description="Test node for management"
        )
        # Create node url
        node_url = reverse('iot_api:iot_general_api-node', args=(node.id, ))
        # Test without header
        get_nh_response = self.client_api.get(
            node_url,
            format='json'
        )
        self.assertTrue(
            get_nh_response.status_code == 403 or 
            get_nh_response.status_code == 401 or 
            get_nh_response.status_code == 400
        )
        # Test with unauthorized token
        header = {'HTTP_CA_TOKEN':node_token}
        get_response = self.client_api.get(
            node_url,
            format='json',
            **header
        )
        self.assertTrue(
            get_nh_response.status_code == 403 or 
            get_nh_response.status_code == 401 or 
            get_nh_response.status_code == 400
        )