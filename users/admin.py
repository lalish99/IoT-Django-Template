from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.forms import GUserCreationForm, GUserInfoChange
import users.models as models

class GeneralAdminUser(UserAdmin):
    add_form = GUserCreationForm
    form = GUserInfoChange
    model = models.GeneralUser
    list_display = ['username', 'email']

admin.site.register(models.GeneralUser, GeneralAdminUser)
