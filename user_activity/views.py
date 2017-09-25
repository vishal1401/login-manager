import datetime
from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import logout_then_login, login
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from user_activity.forms import UserCreationForm
from user_activity.models import UserActivity


class LoginView(View):
    """
        View for login/signup page
    """
    def get(self, *args, **kwargs):
        return self._login(*args, **kwargs)

    def post(self, *args, **kwargs):
        response = self._login(*args, **kwargs)
        request = args[0]

        if request.user.is_authenticated():
            # Creating a user activity object for the user specific to session
            UserActivity.objects.create(user=request.user,
                                        login_time=datetime.datetime.now(),
                                        session_id=request.session.session_key)
        return response

    def _login(self, *args, **kwargs):
        next_url = self.request.GET.get('next', settings.LOGIN_REDIRECT_URL)
        if self.request.user.is_authenticated():
            return HttpResponseRedirect(next_url)
        sign_up_url = '{0}/signup/'.format(settings.APP_URL)
        response = login(*args, extra_context={'sign_up_url': sign_up_url,
                                               'app_url': settings.APP_URL}, **kwargs)
        return response


@method_decorator(csrf_exempt, name='dispatch')
class SignUp(View):
    def get(self, request):
        sign_in_url = '{0}/'.format(settings.APP_URL)
        form = UserCreationForm()
        return render_to_response('registration/signup.html', {'sign_in_url': sign_in_url,
                                                               'form': form})

    def post(self, request):
        form = UserCreationForm(request, request.POST)
        if form.is_valid():
            user = form.save()
            user.backend = ModelBackend
            return HttpResponseRedirect('/dashboard/')
        else:
            sign_in_url = '{0}/'.format(settings.APP_URL)
            return render_to_response('registration/signup.html', {'sign_in_url': sign_in_url,
                                                                   'form': form})


class DashboardView(LoginRequiredMixin, View):
    """
        View for Dashboard page
    """
    @staticmethod
    def get(request):
        # Fetching only past sessions (May include active sessions other than the current one)
        # Order : Recent Login first
        user_sessions = UserActivity.objects.filter(user=request.user)\
            .exclude(session_id=request.session.session_key).order_by('-login_time')

        # Current session UserActivity Object based on session_id
        try:
            current_session = UserActivity.objects.get(user=request.user,
                                                       session_id=request.session.session_key)
        except ObjectDoesNotExist:
            current_session = None
        return render(request, 'dashboard.html', {'sessions': user_sessions,
                                                  'current_session': current_session,
                                                  'total_sessions': user_sessions.count()})


def logout_user(request):
    """
        Terminates current session of the user
        :param request: Request Object
    """
    # Updating the logout time of UserActivity Object belonging to current session
    UserActivity.objects.filter(user=request.user,
                                session_id=request.session.session_key)\
        .update(logout_time=datetime.datetime.now())
    response = logout_then_login(request)
    return response
