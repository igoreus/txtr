from django.contrib.auth.models import User
from django.test import TestCase

from service.models import UserProfile
from service.forms import RegistrationForm, PasswordChangeForm, SubscribeForm

class RegistrationFormTests(TestCase):
    """
        Test the registration form.
    """
    user_data = {'email': 'txtr@txtr.com',
                 'password': 'txtr_password1',
                 'first_name': 'first_name',
                 'last_name': 'last_name',}


    def test_registration(self):
        """
            Test that 'RegistrationForm' if data is valid.
        """
        form = RegistrationForm(data={'email': self.user_data['email'],
                                    'first_name': self.user_data['first_name'],
                                    'last_name': self.user_data['last_name'],
                                    'password1': self.user_data['password'],
                                    'password2': self.user_data['password']}
        )
        self.assertTrue(form.is_valid())
        user = form.register(True)
        self.assertTrue(isinstance(user, User))

    def test_registration_invalid_data(self):
        """
            Test 'RegistrationForm' for case if data is invalid.
        """
        invalid_data = [
            # wrong email
            {'email': 'foo.example.com',
                      'first_name': self.user_data['first_name'],
                      'last_name': self.user_data['last_name'],
                      'password1': self.user_data['password'],
                      'password2': self.user_data['password'],
            },
            # Wrong password: too small
            {'email': self.user_data['email'],
                      'first_name': self.user_data['first_name'],
                      'last_name': self.user_data['last_name'],
                      'password1': 'foo',
                      'password2': 'foo'
            },
            # Wrong password: without number
            {'email': self.user_data['email'],
                      'first_name': self.user_data['first_name'],
                      'last_name': self.user_data['last_name'],
                      'password1': 'foofoofoo',
                      'password2': 'foofoofoo'
            },
            # Wrong password: mismatched passwords.
            {'email': self.user_data['email'],
                      'first_name': self.user_data['first_name'],
                      'last_name': self.user_data['last_name'],
                      'password1': 'foo123',
                      'password2': 'bar123'
            },
            # Empty first and last name.
            {'email': self.user_data['email'],
                      'first_name': '',
                      'last_name': '',
                      'password1': self.user_data['password'],
                      'password2': self.user_data['password']
             },
        ]

        for data in invalid_data:
            form = RegistrationForm(data=data)
            self.assertFalse(form.is_valid())

    def test_registration_unique_email(self):
        """
            Test 'RegistrationForm' for case if email is not unique.
        """
        UserProfile.objects.create_user(**self.user_data)

        form = RegistrationForm(data={'email': self.user_data['email'],
                                      'first_name': self.user_data['first_name'],
                                      'last_name': self.user_data['last_name'],
                                      'password1': self.user_data['password'],
                                      'password2': self.user_data['password']}
        )
        self.assertFalse(form.is_valid())
        form = RegistrationForm(data={'email': 'foo@example.com',
                                      'first_name': self.user_data['first_name'],
                                      'last_name': self.user_data['last_name'],
                                      'password1': self.user_data['password'],
                                      'password2': self.user_data['password']}
        )
        self.assertTrue(form.is_valid())


class PasswordChangeFormTests(TestCase):
    """
        Test the change password form.
    """
    user_data = {'email': 'txtr@txtr.com',
                 'password': 'txtr_password1',
                 'first_name': 'first_name',
                 'last_name': 'last_name',}

    def setUp(self):
        self.user = UserProfile.objects.create_user(**self.user_data)


    def test_change_password(self):
        """
            Test validates password. The  form is inheritor PasswordChangeFormDjango so, other functionality
            must have been tested in Django tests
        """
        invalid_data = [
            # Wrong password: too small
            {'old_password': self.user_data['password'],
             'new_password1': 'foo',
             'new_password2': 'foo'
            },
            # Wrong password: without number
            {'old_password': self.user_data['password'],
             'new_password1': 'foofoofoo',
             'new_password2': 'foofoofoo'
            },
            # Wrong password: mismatched passwords.
            {'old_password': self.user_data['password'],
             'new_password1': 'foo123',
             'new_password2': 'bar123'
            },
        ]

        for data in invalid_data:
            form = PasswordChangeForm(self.user, data)
            self.assertFalse(form.is_valid())


class SubscribeFormTests(TestCase):
    """
        Test the subscribe form.
    """
    user_data = {'email': 'txtr@txtr.com',
                 'password': 'txtr_password1',
                 'first_name': 'first_name',
                 'last_name': 'last_name',}

    def setUp(self):
        self.user = UserProfile.objects.create_user(**self.user_data)

    def test_subscribe(self):
        """
            'SubscribeForm' changes subscription for user.
        """
        form = SubscribeForm(self.user, data={'subscribe': True})
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(self.user.profile.subscribed, True)

    def test_subscribe_initial_data(self):
        """
            Test checks that initial data are correct.
        """
        form = SubscribeForm(self.user)
        self.assertEqual(self.user.profile.subscribed, form.initial['subscribe'])

        self.user.profile.subscribed = True
        form = SubscribeForm(self.user)
        self.assertEqual(self.user.profile.subscribed, form.initial['subscribe'])