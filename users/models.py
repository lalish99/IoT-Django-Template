from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid, hashlib

class GeneralUser(AbstractUser):
    """
    General user model for the project
    """

    class Meta:
	       db_table = 'auth_user'

    def __str__(self):
	       return self.username


class CustomAccessTokens(models.Model):
    """
    Access tokens
    ====
    This tokens can be associated to an user
    in order to allow external connections to
    sections allowed by the user
    """
    def hex_uuid():
        return uuid.uuid4().hex
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=20)
    uuid_token = models.CharField(max_length=36, default=hex_uuid)
    user = models.ForeignKey(
        GeneralUser,
        on_delete=models.CASCADE,
        related_name="user_custom_tokens",
    )


    def save(self, *args, **kwargs):
        self.uuid_token = hashlib.sha256(self.uuid_token.encode()).hexdigest()
        super(CustomAccessTokens, self).save(*args, **kwargs)


    def __str__(self):
        return '{}\'s token for {}'.format(self.user.username, self.name)