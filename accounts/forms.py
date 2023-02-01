from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from core.model_enums import Devices

"""
Form for create signin form
"""


class SigninForm(UserCreationForm):
    email = forms.CharField(max_length=100, required=True,
                            widget=forms.EmailInput())

    device = forms.ChoiceField(choices=Devices.choices)

    class Meta:
        model = User
        fields = ['username', 'device', 'email', 'password1', 'password2']
