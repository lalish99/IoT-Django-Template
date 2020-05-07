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
    node_token = ""
    node_id = None
    sensor_id = None

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
        self.node_token = token.uuid_token
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
            description="Test node for sensor measurement",
        )
        self.node_id = zone.id
        node.access_keys.add(token)
        node.save()
        sensor = models.Sensors.objects.create(
            zone=zone,
            node=node,
            ambiental=False,
            sensor_type=choices.DHT11
        )
        self.sensor_id = sensor.id


    def test_create_get_measures(self):
        """
        Create and get measures of a sensor
        """
        # Validate requirements
        self.assertNotEqual(self.user, None)
        self.assertNotEqual(self.node_token, "")
        self.assertNotEqual(self.node_id, None)
        self.assertNotEqual(self.sensor_id, None)
        # Create url
        url_measure = reverse("iot_api:iot_general_api-measure")
        # Create header
        header = {'HTTP_CA_TOKEN':self.node_token}
        # Count measurements
        number_measures = len(models.Measurement.objects.all())
        # Create new measurements
        measure_data = {
            'sensors':[
                {
                    'id_sensor':self.sensor_id,
                    'value':20,
                    'measurement_type':choices.A_TEMPERATURE
                },
                {
                    'id_sensor':self.sensor_id,
                    'value':2,
                    'measurement_type':choices.B_PRESSURE
                },
                {
                    'id_sensor':self.sensor_id,
                    'value':0.5,
                    'measurement_type':choices.R_HUMIDITY
                }
            ]
        }
        post_response = self.client_api.post(
            url_measure,
            measure_data,
            format='json',
            **header
        )
        self.assertEqual(post_response.status_code, 200) # Measurements created
        self.assertEqual(number_measures + 3, len(models.Measurement.objects.all()))
        measurements = post_response.data['measurements']
        # Create sensor measurements url
        url_sensor_measurements = reverse('iot_api:iot_general_api-sensor-measurements', args=(self.sensor_id,))
        # Get 
        get_response = self.client_api.get(
            url_sensor_measurements,
            format='json',
            **header
        )
        self.assertEqual(get_response.status_code, 200) # Information received
        self.assertEqual(measurements, get_response.data['sensor']['measurements'])