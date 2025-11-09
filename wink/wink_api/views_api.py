"""
wink/wink_api/views_api.py
"""

import datetime
from typing import Union

from django.http import FileResponse
from rest_framework.response import Response
from project import settings


# def set_cookie(response: Union[Response,FileResponse], key: str, value: str, days_expire=7) -> None:
#     if days_expire is None:
#         max_age = 365 * 24 * 60 * 60  # one year
#     else:
#         max_age = days_expire * 24 * 60 * 60
#     expires = datetime.datetime.strftime(
#         datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age),
#         "%a, %d-%b-%Y %H:%M:%S GMT",
#     )
#     response.set_cookie(
#         key,
#         value,
#         max_age=max_age,
#         expires=expires,
#         domain="/",
#         secure=settings.SESSION_COOKIE_SECURE or None,
#     )
