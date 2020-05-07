from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from users.models import GeneralUser, CustomAccessTokens
from IoT.api.views import IoTProjectsViewSet
import IoT.models as models
import IoT.model_choices as choices

class ProjectManagementTestCase(TestCase):
    """
    Test Project management
    project_1 = {
        name:"Test",
        description:"Test project",
        snippet_title:"Test Snippet",
        snippet_image:"image.png"
    }
    project_2 = {
        name:"Test2",
        description:"Test project 2",
        snippet_title:"Test Snippet 2",
        snippet_image:"image2.png"
    }
    """
    user = None
    token = None

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
        self.token = token
        token.save()

    