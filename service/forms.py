from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm as PasswordChangeFormDjango
from django.contrib.auth.models import User
from service.models import UserProfile
from django.contrib.auth import authenticate

class EmailAuthenticationForm(AuthenticationForm):
    """
    Authentication form uses email as login
    """
    username = forms.CharField(label="Email", max_length=75, widget=forms.TextInput(attrs={'class':'vTextField'}))

    def __init__(self, request=None, *args, **kwargs):
        super(EmailAuthenticationForm, self).__init__(request, *args, **kwargs)
        self.fields['password'].widget.attrs = {'class':'vTextField'}


class RegistrationForm(forms.Form):
    """
    Form for registering a new user.

    """
    email = forms.EmailField(label="Email", max_length=75, required=True)
    first_name = forms.CharField(label="First Name", max_length=30, required=True)
    last_name = forms.CharField(label="Last Name", max_length=30, required=True)
    password1 = forms.RegexField(label="Password", min_length=5, widget=forms.PasswordInput(render_value=True),\
        required=True, regex='^.*\d.*$')
    password2 = forms.RegexField(label="Password (again)", widget=forms.PasswordInput(render_value=True),\
        required=True, regex='^.*\d.*$')

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__( *args, **kwargs)
        for key, field in self.fields.items():
            field.widget.attrs = {'class':'vTextField'}

    def clean_email(self):
        """
        Validate the  email.
        """
        if User.objects.filter(email=self.cleaned_data['email'].lower()):
            raise forms.ValidationError("This email address is already exist. Please use another email.")
        return self.cleaned_data['email']

    def clean(self):
        """
        Verify that both passwords are equal.
        """
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError("The two password fields didn't match.")
        return self.cleaned_data

    def register(self, auth = True):
        """
        Registers of new user and authenticates if auth is true.
        """
        user =  UserProfile.objects.create_user(
            self.cleaned_data['email'],
            self.cleaned_data['password1'],
            self.cleaned_data['first_name'],
            self.cleaned_data['last_name']
        )
        if auth and user:
            user = authenticate(username=self.cleaned_data['email'], password = self.cleaned_data['password1'])
        return user

class PasswordChangeForm(PasswordChangeFormDjango):
    """
    Changes User password
    """
    new_password1 = forms.RegexField(label="New password", min_length=5, widget=forms.PasswordInput(render_value=True),\
        required=True, regex='^.*\d.*$')
    new_password2 = forms.RegexField(label="New password confirmation", min_length=5,\
        widget=forms.PasswordInput(render_value=True), required=True, regex='^.*\d.*$')

class SubscribeForm(forms.Form):
    """
    Subscribe or unsubscribe from the service newsletter
    """
    subscribe = forms.BooleanField(required=False, label="Subscribe",)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(SubscribeForm, self).__init__(*args, **kwargs)
        if not len(args):
            self.initial['subscribe'] = user.profile.subscribed

    def save(self, commit=True):
        self.user.profile.subscribed = self.cleaned_data['subscribe']
        if commit:
            self.user.profile.save()
        return self.user