from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.admin import UserAdmin
from users.forms import GUserCreationForm, GUserInfoChange
import users.models as models

class GeneralAdminUser(UserAdmin):
    add_form = GUserCreationForm
    form = GUserInfoChange
    model = models.GeneralUser
    list_display = ['username', 'email']


class GeneralAdminAccessToken(admin.ModelAdmin):
    """
    Custom setup for access token
    ====
    """
    model = models.CustomAccessTokens
    def get_exclude(self, request, obj=None, **kwargs):
        return ['uuid_token']

    def save_model(self, request, obj, form, change):
        messages.add_message(request, messages.INFO, '{}'.format(obj.uuid_token).lower())
        super(GeneralAdminAccessToken, self).save_model(request, obj, form, change)

admin.site.register(models.GeneralUser, GeneralAdminUser)
admin.site.register(models.CustomAccessTokens, GeneralAdminAccessToken)