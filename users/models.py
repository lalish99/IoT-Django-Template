from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models

# Customize this class if you need to change your user model
class GeneralUser(AbstractUser):
    """
    General user model for the project
    """

    class Meta:
	       db_table = 'auth_user'

    def __str__(self):
	       return self.username
