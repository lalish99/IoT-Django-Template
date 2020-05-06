from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from users.models import GeneralUser, CustomAccessTokens
from IoT.api.views import IoTProjectsViewSet
import IoT.models as models
import IoT.model_choices as choices

class FullSetupTest(TestCase):
    """
    Test full setup from user creation to measurement
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

    def ApiZoneCreation(self):
        """
        Test project creation using token
        """
        # Validate we have project id
        self.assertNotEqual(self.project_id, None)
        # Create url
        url_project_zones = reverse('iot_api:iot_general_api-project-zones', args=(self.project_id,))
        # Create headers
        header = {'HTTP_CA_TOKEN': self.project_token}
        # Verify the new project has no zones
        get_response = self.client_api.get(
            url_project_zones,
            format='json',
            **header
        )
        self.assertEqual(get_response.data['project_zones'],[])
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
        self.zone_id = post_response.data['zones'][0]['id'] # Save newly created id


    def test_ambiental_sensor_creation(self):
        self.ApiZoneCreation()
        # Validate we have zone id
        self.assertNotEqual(self.zone_id, None)
