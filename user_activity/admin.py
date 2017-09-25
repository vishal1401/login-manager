from django.contrib import admin

from user_activity.models import UserActivity
from user_activity.models import ActivityUser


class UserActivityAdmin(admin.ModelAdmin):
    """
        UserActivity Model Admin
    """
    list_display = ('user', 'login_time', 'logout_time')

admin.site.register(UserActivity, UserActivityAdmin)

admin.site.register(ActivityUser)
