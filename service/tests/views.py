from django.contrib.auth.models import User
from django.test import TestCase
from django.core import mail
from service.models import UserProfile
from service.forms import RegistrationForm, PasswordChangeForm, SubscribeForm, EmailAuthenticationForm
from django.core.urlresolvers import reverse

class ViewTests(TestCase):
    """
    Test the views.
    """
    user_data = {'email': 'txtr@txtr.com',
                 'password': 'txtr_password1',
                 'first_name': 'first_name',
                 'last_name': 'last_name',}
    def setUp(self):
        self.user = UserProfile.objects.create_user(**self.user_data)
        mail.outbox = []

    def tearDown(self):
        self.user = None
        mail.outbox = []

    def test_home_user_logged(self):
        """
        GET to home view. User is logged
        """
        self.user = self.client.login(username=self.user_data['email'], password=self.user_data['password'])
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'service/home.html')

    def test_home_user_anonymous(self):
        """
        GET to home view. User is not logged
        """
        response = self.client.get(reverse('home'))
        redirect_url = 'http://testserver%s?next=/' % reverse('login')
        self.assertRedirects(response,redirect_url)

    def test_login_user(self):
        """
        GET to login_user view.
        """
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'service/login.html')
        self.failUnless(isinstance(response.context['form'], EmailAuthenticationForm))

    def test_login_user_success(self):
        """
        POST to login_user view with valid data.
        """
        response = self.client.post(reverse('login'),
            data = {'username': self.user_data['email'],
                    'password': self.user_data['password'],
            }
        )
        self.assertRedirects(response, 'http://testserver%s' % reverse('home'))

    def test_login_user_failure(self):
        """
        POST to login_user view with invalid data.
        """
        response = self.client.post(reverse('login'),
            data = {'username': self.user_data['email'],
                    'password': 'foo',
                    }
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].is_valid())

    def test_registration(self):
        """
        GET to registration view.
        """
        response = self.client.get(reverse('registration'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'service/registration.html')
        self.failUnless(isinstance(response.context['form'], RegistrationForm))


    def test_registration_success(self):
        """
        POST to login_user view with valid data.
        """
        response = self.client.post(reverse('registration'),
            data= {'email': 'new_txtr@txtr.com',
                   'first_name': self.user_data['first_name'],
                   'last_name': self.user_data['last_name'],
                   'password1': self.user_data['password'],
                   'password2': self.user_data['password']
            }
        )
        self.assertRedirects(response, 'http://testserver%s' % reverse('home'))
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(len(mail.outbox), 1)

    def test_registration_failure(self):
        """
        POST to login_user view with invalid data (exists email).
        """
        response = self.client.post(reverse('registration'),
            data= self.user_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].is_valid())

        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 0)

    def verification_success(self):
        """
        GET to verification view with valid data.
        """

    def verification_failure(self):
        """
        GET to verification view with invalid data.
        """
