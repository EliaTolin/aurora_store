from django.test import TestCase
from django.contrib.auth.models import User

'''
Tests for login.
'''


class LoginTest(TestCase):

    def setUp(self):
        self.test_user = User.objects.create_user(
            username='elia', password='alfa', email='mail@eliatolin.it')

    def test_login(self):
        # Good credentials
        credentials_good = {'username': 'elia', 'password': 'alfa'}
        self.assertTrue(self.client.login(**credentials_good))

        # False credentials
        credentials_wrong = {'username': 'Test', 'password': 'Test2'}
        self.assertFalse(self.client.login(**credentials_wrong))
