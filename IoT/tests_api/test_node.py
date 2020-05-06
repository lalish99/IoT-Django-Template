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

    def test_node_creation_deletion(self):
        """
        Create a node and delete it via the zone
        """