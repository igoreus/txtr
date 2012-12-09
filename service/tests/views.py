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
        self.client.login(username=self.user_data['email'], password=self.user_data['password'])
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
        self.assertTrue(isinstance(response.context['form'], EmailAuthenticationForm))

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
        self.assertTrue(isinstance(response.context['form'], RegistrationForm))


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

    def test_verification_success(self):
        """
        GET to verification view with valid data.
        """
        response = self.client.get(reverse('verification', kwargs={'key': self.user.profile.verification_key}))
        self.assertTrue(UserProfile.objects.get(user__email=self.user_data['email']).is_verified)
        self.assertEqual(response.status_code, 302)

    def test_verification_failure(self):
        """
        GET to verification view with invalid data.
        """
        response = self.client.get(reverse('verification', kwargs={'key': 'invalidKey'}))
        self.assertEqual(response.status_code, 404)

    def test_settings(self):
        """
        GET to settings view.
        """
        self.client.login(username=self.user_data['email'], password=self.user_data['password'])
        response = self.client.get(reverse('settings'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'service/settings.html')
        self.assertTrue(isinstance(response.context['change_password_form'], PasswordChangeForm))
        self.assertTrue(isinstance(response.context['subscribe_form'], SubscribeForm))

    def test_settings_anonymous(self):
        """
        GET to settings view. User is not logged
        """
        response = self.client.get(reverse('settings'))
        redirect_url = 'http://testserver%s?next=%s' % (reverse('login'), reverse('settings'))
        self.assertRedirects(response,redirect_url)

    def test_settings_task_change_password(self):
        """
        POST to settings view with change_password task.
        """
        new_password = 'new_password1'
        self.client.login(username=self.user_data['email'], password=self.user_data['password'])
        response = self.client.post(reverse('settings'),
            data= {'task': 'change_password',
                   'old_password': self.user_data['password'],
                   'new_password1': new_password,
                   'new_password2': new_password
            },
        )
        self.assertRedirects(response, 'http://testserver%s' % reverse('settings'))
        self.assertTrue(self.client.login(username=self.user_data['email'], password=new_password))

    def test_settings_task_change_password(self):
        """
        POST to settings view with subscribe task.
        """
        self.client.login(username=self.user_data['email'], password=self.user_data['password'])
        response = self.client.post(reverse('settings'),
            data= {'task': 'subscribe',
                   'subscribe': True,
            },
        )
        self.assertRedirects(response, 'http://testserver%s' % reverse('settings'))
        self.assertTrue(UserProfile.objects.get(user__email=self.user_data['email']).subscribed)