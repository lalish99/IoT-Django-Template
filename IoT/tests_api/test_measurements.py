from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from users.models import GeneralUser, CustomAccessTokens
from IoT.api.views import IoTProjectsViewSet
import IoT.models as models
import IoT.model_choices as choices

class MeasurementManagemenetTestCase(TestCase):
    """
    Test api Measurement management
    """
    client_api = APIClient()
    zone_token = None
    zone = None
    node_token = None
    noed = None

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


    def test_create_measurement_zone(self):
        """
        Test Measurement creation sensors without node (ambiental sensors)
        """
        self.assertNotEqual(self.zone_token, None)
        self.assertNotEqual(self.zone, None)
        self.assertNotEqual(self.node_token, None)
        self.assertNotEqual(self.node, None)
        # Create sensors
        sensors = self.CreateSensors()
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
            ms = post_response.data['measurements']
            # Get measurements and validate
            # Create url sensor_measurements
            url_sensor_measurements = reverse('iot_api:iot_general_api-sensor-measurements', args=(sensor.id,))
            get_response = self.client_api.get(
                url_sensor_measurements,
                format="json",
                **header
            )
            self.assertEqual(get_response.status_code, 200) # Gotten correctly
            self.assertEqual(ms, get_response.data['measurements'])

        self.assertEqual(m_count+(len(sensors*nmp_sensor)), len(models.Measurement.objects.all()))


    def test_create_measurement_node(self):
        """
        Test Measurement creation sensors without node (ambiental sensors)
        """
        self.assertNotEqual(self.zone_token, None)
        self.assertNotEqual(self.zone, None)
        self.assertNotEqual(self.node_token, None)
        self.assertNotEqual(self.node, None)
        # Create sensors
        sensors = self.CreateSensors(node=True)
        # Create header
        header = {'HTTP_CA_TOKEN':self.node_token}
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
            ms = post_response.data['measurements']
            # Get measurements and validate
            # Create url sensor_measurements
            url_sensor_measurements = reverse('iot_api:iot_general_api-sensor-measurements', args=(sensor.id,))
            get_response = self.client_api.get(
                url_sensor_measurements,
                format="json",
                **header
            )
            self.assertEqual(get_response.status_code, 200) # Gotten correctly
            self.assertEqual(ms, get_response.data['measurements'])

        self.assertEqual(m_count+(len(sensors*nmp_sensor)), len(models.Measurement.objects.all()))


    def test_unauthorized_measurement_zone(self):
        """
        Test creation of zone measurement with wrong credentials
        """
        # Create sensors
        sensor = self.CreateSensors()[0]
        # Create wrong header
        header = {'HTTP_CA_TOKEN':"test_fake_token"}
        # Count measurements
        m_count = len(models.Measurement.objects.all())
        # Number of measurements per sensor
        nmp_sensor = 3
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
        # Create measurements no header
        post_nh_response = self.client_api.post(
            sensor_url,
            m,
            format="json",
        )
        self.assertTrue(
            post_nh_response.status_code == 403 or 
            post_nh_response.status_code == 401 or 
            post_nh_response.status_code == 400
        )
        self.assertEqual(m_count, len(models.Measurement.objects.all()))
        # Crete wrong header
        post_response = self.client_api.post(
            sensor_url,
            m,
            format="json",
            **header
        )
        self.assertTrue(
            post_response.status_code == 403 or 
            post_response.status_code == 401 or 
            post_response.status_code == 400
        )
        self.assertEqual(m_count, len(models.Measurement.objects.all()))


    def test_unauthorized_measurement_node(self):
        """
        Test creation of zone measurement with wrong credentials
        """
        # Create sensors
        sensor = self.CreateSensors(node=True)[0]
        # Create wrong header
        header = {'HTTP_CA_TOKEN':"test_fake_token"}
        # Count measurements
        m_count = len(models.Measurement.objects.all())
        # Number of measurements per sensor
        nmp_sensor = 3
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
        # Create measurements no header
        post_nh_response = self.client_api.post(
            sensor_url,
            m,
            format="json",
        )
        self.assertTrue(
            post_nh_response.status_code == 403 or 
            post_nh_response.status_code == 401 or 
            post_nh_response.status_code == 400
        )
        self.assertEqual(m_count, len(models.Measurement.objects.all()))
        # Crete wrong header
        post_response = self.client_api.post(
            sensor_url,
            m,
            format="json",
            **header
        )
        self.assertTrue(
            post_response.status_code == 403 or 
            post_response.status_code == 401 or 
            post_response.status_code == 400
        )
        self.assertEqual(m_count, len(models.Measurement.objects.all()))


    def test_unauthorized_sensor_measurements(self):
        """
        Test unauthorized aquisition of sensor measurements
        """
        # Create sensors
        sensor = self.CreateSensors()[0]
        # Create wrong header
        header_fake = {'HTTP_CA_TOKEN':"test_fake_token"}
        header_node = {'HTTP_CA_TOKEN':self.node_token}
        # Count measurements
        m_count = len(models.Measurement.objects.all())
        # Create url
        sensor_url = reverse('iot_api:iot_general_api-sensor-measurements', args=(sensor.id,))
        # Create measurements no header
        get_nh_response = self.client_api.get(
            sensor_url,
            format="json",
        )
        self.assertTrue(
            get_nh_response.status_code == 403 or 
            get_nh_response.status_code == 401 or 
            get_nh_response.status_code == 400
        )
        self.assertEqual(m_count, len(models.Measurement.objects.all()))
        # Crete wrong header
        get_response = self.client_api.get(
            sensor_url,
            format="json",
            **header_fake
        )
        # Try with node header
        get_response = self.client_api.get(
            sensor_url,
            format="json",
            **header_node
        )
        self.assertTrue(
            get_response.status_code == 403 or 
            get_response.status_code == 401 or 
            get_response.status_code == 400
        )
        self.assertEqual(m_count, len(models.Measurement.objects.all()))
        