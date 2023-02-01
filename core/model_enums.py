from django.db import models

'''Enums with categories apps'''


class AppCategories(models.TextChoices):
    cat_sport = 'sport', 'Sport'
    cat_game = 'game', 'Giochi'
    cat_utility = 'utility', 'Utility'
    cat_arcade = 'arcade', 'Arcade'
    cat_weather = 'weather', 'Meteo'
    cat_health = 'health', 'Medicina'
    cat_news = 'news', 'News'
    cat_other = 'other', 'Altro'


'''Enums with devices'''


class Devices(models.TextChoices):
    ios = 'ios', 'iOS'
    android = 'android', 'Android'
