from datetime import datetime
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files import File
from PIL import Image
import io
# Create your tests here.
from .models import App, BillingAddress
from core.model_enums import Devices, AppCategories


class CoreTests(TestCase):
    # Setup tests
    def setUp(self):
        self.user = User.objects.create_user(
            username='elia', password='alfa', email='mail@eliatolin.it')

        self.credential = {'username': 'elia', 'password': 'alfa'}

        self.app = App.objects.create(name="Offertiamo",
                                      description="App di sconti",
                                      image="image",
                                      price=0.0,
                                      category=AppCategories.cat_arcade,
                                      app_id="com.auroradigital.offertiamo",
                                      version="1.0.0",
                                      slug="com.auroradigital.offertiamo",
                                      device=Devices.ios,
                                      developer=self.user,
                                      data=datetime.now(),
                                      ordered=False,
                                      sales_count=10000,
                                      email="eliatolin@gmail.com",
                                      raiting=5.0,
                                      total_rate=1000, )

        self.billing_address = BillingAddress.objects.create(user=self.user,
                                                             country="Italia",
                                                             city="Roma",
                                                             cap="2323",
                                                             route="3232",
                                                             house_number="3232",
                                                             note="",
                                                             default=False,
                                                             )
        self.user_2 = User.objects.create_user(
            username='Test', email='test@test.com', password='test')
        self.crendential_2 = {'username': 'Test', 'password': 'test'}

    '''Test for apps creation with empty fields'''

    def test_app_empty_field_create(self):
        """
        Check if mandatory field are respects
        """
        self.client.login(**self.credential)
        response = self.client.post('/add_app/', {})

        # Check status code
        self.assertEqual(response.status_code, 200)

        # Check template used
        self.assertTemplateUsed(response, 'core/add_app.html')

        # Check if the generated error is corrected and if it is handled correctly.
        # Name field
        self.assertFormError(response, 'form', 'name',
                             'Questo campo è obbligatorio.')
        # Price field
        self.assertFormError(response, 'form', 'price',
                             'Questo campo è obbligatorio.')
        # Category field
        self.assertFormError(response, 'form', 'category',
                             'Questo campo è obbligatorio.')
        # Description field
        self.assertFormError(response, 'form', 'description',
                             'Questo campo è obbligatorio.')
        # Image field
        self.assertFormError(response, 'form', 'image',
                             'Questo campo è obbligatorio.')
        # Device field
        self.assertFormError(response, 'form', 'device',
                             'Questo campo è obbligatorio.')
        # App_id field
        self.assertFormError(response, 'form', 'app_id',
                             'Questo campo è obbligatorio.')
        # Version field
        self.assertFormError(response, 'form', 'version',
                             'Questo campo è obbligatorio.')
        # Email field
        self.assertFormError(response, 'form', 'email',
                             'Questo campo è obbligatorio.')

    '''Test for apps creation'''

    def test_app_create(self):
        self.client.login(**self.credential)

        # Create random image
        image = Image.new("RGB", size=(400, 400), color=(255, 0, 0))
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        # Form data
        form_data = {'name': 'offertiamo',
                     'app_id': 'com.aurorastore.offertiamo',
                     'version': '1.0.0',
                     'email': 'mail@eliatolin.it',
                     'price': '10',
                     'category': AppCategories.cat_arcade,
                     'description': 'app bellissima',
                     'image': SimpleUploadedFile(name='test_image.png', content=buffer.read(),
                                                 content_type='image/png'),
                     'device': Devices.android,
                     'developer_id': self.user.pk}

        response = self.client.post('/add_app/', form_data)
        # If it redirects, it means it was successful.
        self.assertRedirects(response, '/')
        self.assertEqual(response.status_code, 302)

    '''
    Test for check delete app
    '''

    def test_app_delete(self):
        # With authenticated user
        self.client.login(**self.credential)
        response = self.client.get('/app/{}/delete/'.format(str(self.app.id)))
        # If 200, not exist, it not works.
        self.assertEqual(response.status_code, 200)
        # Not deleted
        self.assertEqual(len(App.objects.filter(pk=self.app.id).all()), 1)
        response = self.client.post(
            '/app/{}/delete/'.format(str(self.app.id)), {})
        # If it redirects, it means it was successful.
        self.assertRedirects(
            response, "/user/{}/".format(self.user.username))
        self.assertEqual(response.status_code, 302)
        # Check if app it deleted
        self.assertEqual(len(App.objects.filter(pk=self.app.id).all()), 0)
        self.client.logout()

        # With authenticated user but not creator of app
        self.client.login(**self.crendential_2)
        response = self.client.get('/app/{}/delete/'.format(str(self.app.id)))
        self.assertTemplateNotUsed(response, 'core/app_delete.html')

    '''
    An unlogged in user is redirected to login.
    '''

    def test_login_required(self):
        response = self.client.get('/add_app/')
        # Check redirect
        self.assertRedirects(
            response, '/accounts/login/?next=/add_app/')
        # Exist but not allowed, redirect in login page
        self.assertEqual(response.status_code, 302)

    '''
    Test for check users profiles with authenticated and unauthenticated user. 
    '''

    def test_user_profile(self):
        # My profile
        self.client.login(**self.credential)
        response = self.client.get('/user/{}/'.format(self.user.username))
        self.assertTemplateUsed(response, 'core/profile.html')
        self.assertTrue(response.status_code, 200)

        # Other profiles
        response = self.client.get(
            '/otheruser/{}/'.format(self.user_2.username))
        self.assertTemplateNotUsed(response, 'core/profile.html')
        self.assertTemplateUsed(response, 'core/user_profile.html')

        # With unauthenticated user
        self.client.logout()
        response = self.client.get('/otheruser/{}/'.format(self.user.username))
        self.assertTemplateUsed(response, 'core/user_profile.html')
        self.assertTrue(response.status_code, 200)

    '''
    Test for change billing address 
    '''

    def test_address_change(self):
        # With auth user
        self.client.login(**self.credential)
        # If 200, not exist, it not works.
        response = self.client.get(
            '/user/address/{}/delete/'.format(str(self.billing_address.id)))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            '/user/address/{}/modify/'.format(str(self.billing_address.id)), {})

        # Check if the generated error is corrected and if it is handled correctly.
        # City field
        self.assertFormError(response, 'form', 'city',
                             'Questo campo è obbligatorio.')
        # Route field
        self.assertFormError(response, 'form', 'route',
                             'Questo campo è obbligatorio.')
        # Country field
        self.assertFormError(response, 'form', 'country',
                             'Questo campo è obbligatorio.')
        # Cap field
        self.assertFormError(response, 'form', 'cap',
                             'Questo campo è obbligatorio.')

        # Default is not mandatory

        response = self.client.post('/user/address/{}/modify/'.format(str(self.billing_address.id)),
                                    {'city': 'roma', 'route': 'turbina', 'country': 'it', 'cap': '11444'})
        # If it redirects, it means it was successful.
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, '/user/{}/address_page/'.format(self.user.username))
        self.client.logout()

        # Authenticated user but other user's address
        self.client.login(**self.crendential_2)
        response = self.client.get(
            '/user/address/{}/modify/'.format(str(self.billing_address.id)))
        # Redirect in homepage
        self.assertTemplateUsed(response, 'core/homepage.html')
        self.assertTemplateNotUsed(response, 'accounts/address_change.html')

    ''' 
    Test for delete user's addresses
    '''

    def test_address_delete(self):
        # User authenticated
        self.client.login(**self.credential)
        response = self.client.get(
            '/user/address/{}/delete/'.format(str(self.billing_address.id)))
        # If 200, not exist, it not works.
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            '/user/address/{}/delete/'.format(str(self.billing_address.id)), {})
        # If it redirects, it means it was successful.
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, '/user/{}/address_page/'.format(self.user.username))
        self.client.logout()

        # Authenticated user but other user's address
        self.client.login(**self.crendential_2)
        response = self.client.get(
            '/user/address/{}/delete/'.format(str(self.billing_address.id)))
        # Not allowed
        self.assertTemplateNotUsed(response, 'accounts/address_delete.html')
