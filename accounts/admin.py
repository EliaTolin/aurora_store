from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()

admin.site.register(UserProfile)
