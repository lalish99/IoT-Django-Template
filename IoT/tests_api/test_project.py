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
    client_api = APIClient()
    user = None
    token = None
    token_obj = None

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
        self.token = token.uuid_token
        self.token_obj = token
        token.save()

    def test_projects_access(self):
        """
        Test permissions for users projects list retrival
        """
        # Verify information
        self.assertNotEqual(self.user, None)
        self.assertNotEqual(self.token, None)
        self.assertNotEqual(self.token_obj, None)
        # Count projects
        project_count = len(models.Projects.objects.all())
        # Create multiple projects
        projects = []
        for x in range(5):
            projects.append(
                models.Projects.objects.create(
                    user=self.user,
                    name='Test{}'.format(x),
                    description='Test project'.format(x),
                    snippet_title='Test Snippet',
                    snippet_image='image.png',
                )
            )
        # Add auth tokens
        projects[0].access_keys.add(self.token_obj)
        projects[1].access_keys.add(self.token_obj)
        # Create url
        url_projects = reverse('iot_api:iot_general_api-projects')
        # Create header 
        header = {'HTTP_CA_TOKEN':self.token}
        # Ask for token projects
        get_response = self.client_api.get(
            url_projects,
            format='json',
            **header
        )
        self.assertEqual(len(get_response.data['projects']), 2) # Only two projects allowed
        projects[0].delete()
        projects[1].delete()
        del projects[1]
        del projects[0]
        # Ask for token projects
        get_response = self.client_api.get(
            url_projects,
            format='json',
            **header
        )
        self.assertEqual(len(get_response.data['projects']), 0) # Only two projects allowed
        for p in projects:
            p.delete()
        self.assertEqual(len(models.Projects.objects.all()), project_count) #
    

    def test_unauthorized_project_detail(self):
        """
        Test information obtention failure with unauthorized request
        """
        # Verify information
        self.assertNotEqual(self.user, None)
        self.assertNotEqual(self.token, None)
        self.assertNotEqual(self.token_obj, None)
        # Create projects
        projects = []
        for x in range(3):
            projects.append(
                models.Projects.objects.create(
                    user=self.user,
                    name='Test{}'.format(x),
                    description='Test project'.format(x),
                    snippet_title='Test Snippet',
                    snippet_image='image.png',
                )
            )
        # Create url
        url_project = reverse('iot_api:iot_general_api-project', args=(projects[0].id,))
        # Ask for information without token header
        get_nh_response = self.client_api.get(
            url_project,
            format='json'
        )
        self.assertTrue(
            get_nh_response.status_code == 403 or 
            get_nh_response.status_code == 401 or 
            get_nh_response.status_code == 400
        )
        # Test with unauthorized token
        header = {'HTTP_CA_TOKEN':self.token}
        get_response = self.client_api.get(
            url_project,
            format='json',
            **header
        )
        self.assertTrue(
            get_response.status_code == 403 or 
            get_response.status_code == 401 or 
            get_response.status_code == 400
        )


    def test_unauthorized_project_zones(self):
        """
        Attempt to
        * Create zones with unauthorized project token
        * Delete zones of different project
        * Get zones of project with bad credentials
        """
        # Verify information
        self.assertNotEqual(self.user, None)
        self.assertNotEqual(self.token, None)
        self.assertNotEqual(self.token_obj, None)
        project = models.Projects.objects.create(
                    user=self.user,
                    name='Test{} UA_Z',
                    description='Test project UA_Z',
                    snippet_title='Test Snippet',
                    snippet_image='image.png',
                )
        # Create zones
        zones = []
        for z in range(3):
            zones.append(
                models.Zones.objects.create(
                    name="Updated name zone {}".format(z),
                    description="New updated zone {} description".format(z),
                    project=project,
                )
            )
        project.project_zones.set(zones)
        # Create project zones url
        url_project_zones = reverse('iot_api:iot_general_api-project-zones', args=(project.id,))
        # Post data
        zone_data = {
            "zones":[
                {
                    "name":"Test Zone 1",
                    "description":"First test zone created from api"
                }
            ]
        }
        # Create no token
        post_nh_response = self.client_api.post(
            url_project_zones,
            zone_data,
            format="json"
        )
        self.assertTrue(
            post_nh_response.status_code == 403 or 
            post_nh_response.status_code == 401 or 
            post_nh_response.status_code == 400
        )
        # Create wrong token
        header = {'HTTP_CA_TOKEN':self.token}
        # Create no token
        post_response = self.client_api.post(
            url_project_zones,
            zone_data,
            format="json",
            **header
        )
        self.assertTrue(
            post_response.status_code == 403 or 
            post_response.status_code == 401 or 
            post_response.status_code == 400
        )
        # Attempt deletion of other project zones
        zones_to_delete = {
            "zones":[{"id_zone":z.id} for z in zones]
        }
        # No token
        delete_nh_response = self.client_api.delete(
            url_project_zones,
            zone_data,
            format="json"
        )
        self.assertTrue(
            delete_nh_response.status_code == 403 or 
            delete_nh_response.status_code == 401 or 
            delete_nh_response.status_code == 400
        )
        # Wrong token
        delete_response = self.client_api.delete(
            url_project_zones,
            zone_data,
            format="json",
            **header
        )
        self.assertTrue(
            delete_response.status_code == 403 or 
            delete_response.status_code == 401 or 
            delete_response.status_code == 400
        )
        # Attempt to get information no header
        get_nh_response = self.client_api.get(
            url_project_zones,
            format="json"
        )
        self.assertTrue(
            get_nh_response.status_code == 403 or 
            get_nh_response.status_code == 401 or 
            get_nh_response.status_code == 400
        )
        # Wrong token
        get_response = self.client_api.get(
            url_project_zones,
            format="json",
            **header
        )
        self.assertTrue(
            get_response.status_code == 403 or 
            get_response.status_code == 401 or 
            get_response.status_code == 400
        )