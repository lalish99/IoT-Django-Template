from django.test import TestCase
from django.utils import timezone
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from users.models import GeneralUser, CustomAccessTokens
from IoT.api.views import IoTProjectsViewSet
import IoT.models as models
import IoT.model_choices as choices
import datetime
import pytz

class SensorManagementTestCase(TestCase):
    """
    Test api Sensor management
    """
    client_api = APIClient()
    zone_token = None
    zone = None
    node_token = None
    node = None


    def CreateSensors(self, n=3, node=False):
        """
        Create n sensors for self.zone and optionally self.node
        """
        self.assertNotEqual(self.zone, None)
        self.assertNotEqual(self.node, None)
        # Create zone
        sensors = []
        for s in range(n):
            # Create node
            sensors.append(
                models.Sensors.objects.create(
                    zone=self.zone,
                    node=self.node if node else None,
                    sensor_type=choices.DHT22,
                    ambiental=True if node else False
                )
            )
        return sensors


    def setUp(self):
        # Create User
        user = GeneralUser.objects.create_user(
            username = 'TUMeasurement',
            password = "123Password",
            email = 'test@test.com'
        )
        # Create project
        project = models.Projects.objects.create(
            user=user,
            name='Test',
            description='Test project',
            snippet_title='Test Snippet',
            snippet_image='image.png',
        )
        # Create and save zone token
        token = CustomAccessTokens(
            user=user,
            name="testToken"
        )
        self.zone_token = token.uuid_token
        zone = models.Zones.objects.create(
            project=project,
            name='Test zone',
            description='Test zone for node management',
        )
        self.zone = zone
        token.save()
        zone.access_keys.add(token)
        zone.save()
        # Create and save node token
        token = CustomAccessTokens(
            user=user,
            name="testToken"
        )
        self.node_token = token.uuid_token
        node = models.Node.objects.create(
            zone=zone,
            name="Test node",
            description="Test node for test cases"
        )
        self.node = node
        token.save()
        node.access_keys.add(token)
        node.save()


    def test_sensor_get_delete(self):
        """
        Test getting and deleting a sensor
        """
        self.assertNotEqual(self.zone_token, None)
        self.assertNotEqual(self.node_token, None)
        # Count initial sensors
        i_sensor_count = len(models.Sensors.objects.all())
        # Create sensors
        sensors = self.CreateSensors()
        # Create header
        header = {'HTTP_CA_TOKEN':self.zone_token}
        # Count sensors
        sensor_count = len(models.Sensors.objects.all())
        # Loop sensors get their info and delete them
        for i, sensor in enumerate(sensors):
            # Create url
            url_sensor = reverse('iot_api:iot_general_api-sensor', args=(sensor.id,))
            # Get sensor
            get_response = self.client_api.get(
                url_sensor,
                format="json",
                **header
            )
            self.assertEqual(get_response.status_code, 200)
            self.assertNotEqual(get_response.data, None)
            self.assertNotEqual(get_response.data, [])
            self.assertNotEqual(get_response.data, {})
            # Delete response
            delete_response = self.client_api.delete(
                url_sensor,
                format="json",
                **header
            )
            self.assertEqual(delete_response.status_code, 200)
            self.assertEqual(sensor_count - (i+1), len(models.Sensors.objects.all()))

        self.assertEqual(i_sensor_count, len(models.Sensors.objects.all()))


    def test_get_filtered_measurements(self):
        """
        Get filtered measurements by date    
        """
        self.assertNotEqual(self.zone_token, None)
        self.assertNotEqual(self.zone, None)
        self.assertNotEqual(self.node_token, None)
        self.assertNotEqual(self.node, None)
        # Create sensors
        sensors = self.CreateSensors(n=1)
        # Create header
        header = {'HTTP_CA_TOKEN':self.zone_token}
        # Count measurements
        m_count = len(models.Measurement.objects.all())
        # Number of measurements per sensor
        nmp_sensor = 3
        # Test creating measurements for every sensor in sensors
        for sensor in sensors:
            # Create url
            sensor_url = reverse('iot_api:iot_general_api-measure')
            # Measurements
            m = {
                'sensors':[{
                    'value':30 + (x**2),
                    'id_sensor':sensor.id,
                    'measurement_type':choices.A_TEMPERATURE
                } for x in range(nmp_sensor)]
            }
            # Create measurements
            post_response = self.client_api.post(
                sensor_url,
                m,
                format="json",
                **header
            )
            self.assertEqual(post_response.status_code, 201) # Measurements created
            today = timezone.now()
            y = today.year
            m = today.month
            d = today.day
            get_parameters = {
                "y":y,
                "m":m,
                "d":d
            }
            # Create url
            url_sensor_measurements = reverse('iot_api:iot_general_api-sensor-measurements', args=(sensor.id,))
            # Attemt to get filtered measurements current date
            get_response = self.client_api.get(
                url_sensor_measurements,
                get_parameters,
                format="json",
                **header
            )
            self.assertEqual(get_response.status_code, 200)
            for mesasurement in get_response.data["measurements"]:
                str_date = mesasurement["created_at"].split("T")[0]
                m_date = datetime.datetime.strptime(str_date,"%Y-%m-%d")
                self.assertEqual(y, m_date.year)
                self.assertEqual(m, m_date.month)
                self.assertEqual(d, m_date.day)
            # Attemt to get filtered measurements wrong date
            get_w_parameters = {
                "y":y,
                "m":m+1 if m+1 <= 12 else m-1,
                "d":d
            }
            get_w_response = self.client_api.get(
                url_sensor_measurements,
                get_w_parameters,
                format="json",
                **header
            )
            self.assertEqual(get_w_response.status_code, 200)
            self.assertEqual(get_w_response.data["measurements"], [])



    def test_unauthorized_sensor(self):
        """
        Test unauthorized attempts to acces sensor info
        """
        self.assertNotEqual(self.zone_token, None)
        self.assertNotEqual(self.node_token, None)
        # Create sensors
        sensors = self.CreateSensors(n=1)
        # Count sensors
        sensor_count = len(models.Sensors.objects.all())
        # Loop sensors attempt to get their info and delete them
        for i, sensor in enumerate(sensors):
            # Create url
            url_sensor = reverse('iot_api:iot_general_api-sensor', args=(sensor.id,))
            # Create fake header
            header = {'HTTP_CA_TOKEN':"FAKEACCESSTOKEN"}
            # Attempt to get without header
            get_nh_response = self.client_api.get(
                url_sensor,
                format="json"
            )
            self.assertTrue(
                get_nh_response.status_code == 403 or 
                get_nh_response.status_code == 401 or 
                get_nh_response.status_code == 400
            )
            self.assertEqual(sensor_count, len(models.Sensors.objects.all()))
            # Attempt wrong header
            get_response = self.client_api.get(
                url_sensor,
                format="json",
                **header
            )
            self.assertTrue(
                get_response.status_code == 403 or 
                get_response.status_code == 401 or 
                get_response.status_code == 400
            )
            self.assertEqual(sensor_count, len(models.Sensors.objects.all()))
            # Attempt delete without header
            delete_nh_response = self.client_api.delete(
                url_sensor,
                format="json"
            )
            self.assertTrue(
                delete_nh_response.status_code == 403 or 
                delete_nh_response.status_code == 401 or 
                delete_nh_response.status_code == 400
            )
            self.assertEqual(sensor_count, len(models.Sensors.objects.all()))
            # Attempt wrong header
            delete_response = self.client_api.delete(
                url_sensor,
                format="json",
                **header
            )
            self.assertTrue(
                delete_response.status_code == 403 or 
                delete_response.status_code == 401 or 
                delete_response.status_code == 400
            )
            self.assertEqual(sensor_count, len(models.Sensors.objects.all()))

        self.assertEqual(sensor_count, len(models.Sensors.objects.all()))

