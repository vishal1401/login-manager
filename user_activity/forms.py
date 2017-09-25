from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from user_activity.models import ActivityUser


class UserCreationForm(forms.ModelForm):
    """
        A form that creates a user, with no privileges, from the given username and
        password.
    """
    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super(UserCreationForm, self).__init__(*args, **kwargs)

    class Meta:
        model = ActivityUser
        fields = ("email", "first_name", "password", "mobile")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        # If user exists with the provided email raise Validation Error
        # Else return the email
        try:
            User.objects.get(email=email)
            raise forms.ValidationError("A user with that email already exists",
                                        code='mail_exists')
        except ObjectDoesNotExist:
            return email

    def clean_username(self):
        username = self.cleaned_data.get("email")
        # If user exists with the provided username raise Validation Error
        # Else return the email
        try:
            User.objects.get(username=username)
            raise forms.ValidationError("Username already exists", code='username_exists')
        except ObjectDoesNotExist:
            return username

    def clean_first_name(self):
        name = self.cleaned_data.get("first_name")
        if name:
            return name
        return ''

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.username = self.clean_username()
        user.email = self.clean_email()
        print self.clean_email(), "hereee"
        user.first_name = self.clean_first_name()
        user.set_password(user.password)
        user.save()
        return user

