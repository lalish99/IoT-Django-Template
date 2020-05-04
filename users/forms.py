from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from users.models import GeneralUser

class GUserCreationForm(UserCreationForm):
    """
    Form for general user creation
    """
    class Meta(UserCreationForm):
    	model = GeneralUser
    	fields = ('username', 'first_name',
            'email',
        )

class GUserInfoChange(UserChangeForm):
    """
    Form for applying general changes
    to an users information
    """
    class Meta(UserChangeForm):
        model = GeneralUser
        fields = ('username', 'email')
