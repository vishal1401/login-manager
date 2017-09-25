import uuid as uuid
from django.contrib.auth.models import User
from django.db import models


class ActivityUser(User):
    mobile = models.BigIntegerField()


class UserActivity(models.Model):
    """
        Model to store user activity details
    """
    user = models.ForeignKey(User)
    login_time = models.DateTimeField()
    logout_time = models.DateTimeField(null=True)
    uuid = models.UUIDField(default=uuid.uuid4)
    session_id = models.CharField(max_length=63)
