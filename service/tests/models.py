import re
from django.core import mail
from django.contrib.auth.models import User
from django.test import TestCase

from service.models import UserProfile

class UserProfileModelTests(TestCase):
    """
    Test the model and manager used in the default backend.

    """
    user_data = {'email': 'txtr@txtr.com',
                 'password': 'txtr_password',
                 'first_name': 'first_name',
                 'last_name': 'last_name',
                 }

    def setUp(self):
        pass

    def tearDown(self):
        mail.outbox = []

    def test_create_profile(self):
        """
        Creating a new user profile.
        """
        new_user = User.objects.create_user('username', self.user_data['email'], self.user_data['password'])
        new_user.first_name, new_user.last_name = self.user_data['first_name'], self.user_data['last_name']
        new_user.save()

        user_profile = UserProfile.objects.create(user=new_user)

        self.assertEqual(UserProfile.objects.count(), 1)
        self.assertEqual(user_profile.user.id, new_user.id)
        self.assertEqual(unicode(user_profile), '%s %s' % (new_user.first_name, new_user.last_name))
        self.assertEqual(user_profile.subscribed, False)
        self.assertTrue(re.match('^[a-f0-9]{40}$', user_profile.verification_key))
        self.assertFalse(user_profile.is_verified)

    def test_create_user(self):
        """
        Creating a new user
        """
        new_user = UserProfile.objects.create_user(**self.user_data)

        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(new_user.username, UserProfile.objects._create_fake_username(self.user_data['email']))
        self.assertEqual(new_user.email, self.user_data['email'])
        self.assertTrue(new_user.check_password(self.user_data['password']))
        self.assertTrue(new_user.is_active)

    def test_create_fake_username(self):
        """
        Creates fake username for user who use email as login
        """
        self.assertTrue(re.match('^[a-f0-9]{30}$', UserProfile.objects._create_fake_username(self.user_data['email'])))

    def test_create_user_email(self):
        """
        Creating new user and sending verification email.

        """
        new_user = UserProfile.objects.create_user(**self.user_data)
        self.assertEqual(mail.outbox[0].to, [new_user.email])
        self.assertEqual(len(mail.outbox), 1)


    def test_valid_verification(self):
        """
        Verifies user email when key is valid
        """
        new_user = UserProfile.objects.create_user(**self.user_data)
        updated_user = UserProfile.objects.verification(new_user.profile.verification_key)

        self.assertTrue(isinstance(updated_user, User))
        self.assertEqual(updated_user.profile.verification_key, UserProfile.VERIFIED)

    def test_invalid_verification(self):
        """
        Verifies user email when key is valid
        """
        result = UserProfile.objects.verification('invalid_key')
        self.assertFalse(result)

    def test_is_verified(self):
        """
        Checks whether user is already verified
        """
        new_user = UserProfile.objects.create_user(**self.user_data)
        updated_user = UserProfile.objects.verification(new_user.profile.verification_key)
        self.assertTrue(updated_user.profile.is_verified)