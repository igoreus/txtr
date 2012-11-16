from django.db import models
import hashlib
import time
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail, EmailMultiAlternatives
from django.contrib.auth.models import User
from django.conf import settings

class UserProfileManager(models.Manager):
    """
    Custom Manager for UserProfile model
    """
    def create_user(self, email, password, first_name, last_name):
        """
        Creates new user
        """
        new_user = User.objects.create_user(self._create_fake_username(email), email, password)
        new_user.first_name, new_user.last_name = first_name, last_name
        new_user.save()

        user_profile = self.create(user=new_user)
        user_profile.send_email()
        return new_user

    def create(self, **kwargs):
        """
        Creates new user profile.
        """
        kwargs['verification_key'] = self._create_verification_key(kwargs['user'])
        return super(UserProfileManager, self).create(**kwargs)


    def _create_fake_username(self, email):
        return hashlib.sha1(email).hexdigest()[:30]

    def _get_salt(self):
        return hashlib.sha1(str(time.time())).hexdigest()[:5]

    def _create_verification_key(self, user):
        return hashlib.sha1(self._get_salt() + user.email).hexdigest()

    def verification(self, verification_key):
        """
        Validates an verification key and sets profile as verified
        """
        try:
            user_profile = self.get(verification_key=verification_key)
        except self.model.DoesNotExist:
            return False
        user_profile.verification_key = self.model.VERIFIED
        user_profile.save()
        return user_profile.user

class UserProfile(models.Model):
    """
    Keeps needed additional user data.
    """
    VERIFIED = 'VERIFIED'

    objects = UserProfileManager()

    user = models.OneToOneField(User, related_name='profile')
    verification_key = models.CharField(max_length=40)
    subscribed = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%s %s' % (self.user.first_name, self.user.last_name)

    @property
    def is_verified(self):
        return self.verification_key == self.VERIFIED

    def send_email(self):
        """
        Sends an email with verification data
        """
        context = {
            'user': self.user,
            'host': settings.HOST,
            'verification_key': self.verification_key,
        }
        subject = u'Welcome, %s' % self.user.last_name
        html_content = render_to_string('service/mail/verification_email.html',context)
        msg = EmailMultiAlternatives(subject, strip_tags(html_content), settings.EMAIL_FROM_DEFAULT, [self.user.email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
