from users.models import CustomAccessTokens
from rest_framework import authentication
from rest_framework import exceptions
import hashlib

class CAccessTokenRestAuth(authentication.BaseAuthentication):
    """
    Para proyectos mas avanzados implementar capa intermedia
    Cache, PRIMARY KEY
    Add invalidate field 
    Expiration date
    """
    def authenticate(self, request):
        token = request.META.get('HTTP_CA_TOKEN')
        if not token:
            token=request.META.get('HTTP_ca_token')
        if token:
            token = token.lower()
        if not token:
            return None

        try:
            hashed_token = hashlib.sha256(token.encode()).hexdigest()
            token = CustomAccessTokens.objects.get(uuid_token=hashed_token)
            user = token.user
        except CustomAccessTokens.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such token')

        return (user, token)