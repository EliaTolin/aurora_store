from django.contrib.auth.models import User
from django.db import models
from core.model_enums import Devices, AppCategories
from core.models import App

'''User profile model'''


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile")
    app = models.ManyToManyField(App)

    user_device = models.CharField(choices=Devices.choices, max_length=20)

    def __str__(self):
        return self.user.username
