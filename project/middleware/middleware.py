"""
project/middleware.py
"""

import logging
from logs import configure_logging
from django.http import HttpResponseForbidden
from django.conf import settings


log = logging.getLogger(__name__)
configure_logging(logging.INFO)


class SafeHostMiddleware:
    """
    Middleware of security - check the allowed hosts.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(":")[0]

        safe_hosts = getattr(settings, "ALLOWED_HOSTS", None)


        if host not in safe_hosts:
            log.info(f"Blocked request from unauthorized host: {host}")
            return HttpResponseForbidden("Access denied")

        return self.get_response(request)
