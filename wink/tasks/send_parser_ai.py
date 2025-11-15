"""
wink/tasks/send_parser_ai.py
"""

import logging
from typing import Any, TypedDict

from rest_framework import status
from rest_framework.response import Response

from logs import configure_logging
from project.settings import APP_PROTOCOL, APP_HOST, APP_PORT
from wink.winkClient import AsyncHttpClient, HttpRequest

log = logging.getLogger(__name__)
configure_logging(logging.INFO)


class FileData(TypedDict):
    file_data: Any


async def post_data_parser(parser_data: FileData, refer: str) -> Response:

    global response
    print("=========Верните rsponse.headers['X-Refer-Key'] ===")
    try:

        client = AsyncHttpClient()
        response_csrf = await client.request(
            HttpRequest.GET.value,
            f"{APP_PROTOCOL}://{APP_HOST}:{APP_PORT}/api/v1/wink/csrftoken/",
        )
        response = await client.request(
            HttpRequest.POST.value,
            f"{APP_PROTOCOL}://{APP_HOST}:{APP_PORT}/api/v1/wink/record/",
            headers={
                "X-CSRFToken": response_csrf.body["csrfToken"],
                "X-Refer-Key": refer,
            },
            data=parser_data,
        )

        # "========= Может вернуть ошибку. Тут не знаю в каком виде он вернет данные (в теле client.request)"
        # просто словрь или json-строка будет
        # вроде всё. будут ошибки описшите. и логи отправьте
        #  ==============================
        response.status_code = status.HTTP_200_OK
        return response
    except Exception as e:

        response.status_code = status.HTTP_404_NOT_FOUND
        log.error("[%s]: Error => %s", (post_data_parser.__name__, e.args[0]))
        return response
