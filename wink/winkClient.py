"""
wink/winkClient.py
"""

import asyncio
import json
import logging

import aiohttp

from typing import Dict, Any, Optional, Union
from rest_framework.response import Response
from rest_framework import status
from logs import configure_logging
from enum import Enum

log = logging.getLogger(__name__)
configure_logging(logging.INFO)


class HttpRequest(Enum):
    GET = "GET"
    POST = "POST"


class RouterPath(Enum):
    PATH_GET_KEY = "/api/v1/wink/get/<str:refer>/"
    PATH_FOR_GET = "/api/v1/wink/download/<str:refer>/"
    PATH_FOR_POST = "/api/v1/wink/record/"


class ContentType(Enum):
    DEFAULT = "application/json"


class AsyncHttpClient:
    message = "AsyncHttpClient"

    def __init__(self, timeout: int = 30, verify_ssl: bool = True) -> None:
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.verify_ssl = verify_ssl
        self.headers = {
            "Wink-Aget": "AsyncHttpClient/1.0",
            "Accept": ContentType.DEFAULT.value,
            "Content-Type": ContentType.DEFAULT.value,
        }

    async def request(
        self,
        method: str,
        url: str,
        data: Optional[Union[Dict[str, Any], Any]] = None,
        json_data: Optional[Union[Dict[str, Any], Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        auth: Optional[aiohttp.BasicAuth] = None,
    ) -> Response:
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)
        error_text = "[%s]:" % self.request.__name__
        try:
            async with aiohttp.ClientSession(
                timeout=self.timeout, headers=request_headers
            ) as session:
                try:
                    # ========== clear parameter passing
                    async with session.request(
                        method=method,
                        url=url,
                        data=data,
                        json=json_data,
                        auth=auth,
                        ssl=None if self.verify_ssl else False,
                    ) as response:
                        content_type = response.headers.get("Content-Type", "").lower()
                        content = ""
                        #  ========== Try to parse JSON, fall back to text
                        if "application/json" in content_type:
                            try:
                                context = await response.json()

                            except Exception as e:
                                log.error(
                                    f"{error_text} Error => Failed to parse JSON: {e.args[0]}, falling back to text"
                                )
                                content = await response.text()
                        elif (
                            "application/pdf" in content_type
                            or "image/" in content_type
                            or "application/octet-stream" in content_type
                        ):
                            #  ========== b data ===========
                            context = await response.read()
                            response_content = context
                            media_type = content_type
                        elif any(
                            text_type in content_type
                            for text_type in [
                                "text/",
                                "application/xml",
                                "application/javascript",
                            ]
                        ):
                            #  ========== Handle text-based responses
                            content = await response.text()
                        else:
                            #  ========== Tex data  ==========
                            try:
                                context = await response.text()
                                response_content = context.encode("utf-8")
                                media_type = content_type or "text/plain"
                            except UnicodeDecodeError as e:
                                log.error(
                                    f"{error_text} Error => UnicodeDecodeError: {e.args[0]}, falling back to text"
                                )
                                context = await response.read()
                                response_content = context
                                media_type = "application/octet-stream"
                        # FIX: Properly handle content encoding
                        if isinstance(context, (dict, list)):
                            #  ========== Convert dict/list to JSON string and then encode to bytes
                            response_content = json.dumps(context).encode("utf-8")
                            media_type = "application/json"
                        else:
                            #  ========== If it's already a string, encode to bytes
                            response_content = (
                                context.encode("utf-8")
                                if isinstance(context, str)
                                else context
                            )
                            media_type = content_type or "text/plain"
                        return Response(
                            data=response_content,
                            status=response.status,
                            headers=dict(response.headers),
                            content_type=media_type,
                        )
                except asyncio.TimeoutError:
                    error_msg = f"Request timeout after {self.timeout} seconds"
                    log.error(
                        f"{error_text} Error => {self.message}.{self.request.__name__} ERROR => {error_msg}"
                    )
                    return Response(
                        data={"errors": error_msg},
                        status=status.HTTP_408_REQUEST_TIMEOUT,
                    )

                except aiohttp.ClientError as e:
                    error_msg = f"HTTP client error: {str(e)}"
                    log.error(
                        f" {error_text} Error => {self.message}.{self.request.__name__} ERROR => {error_msg}"
                    )
                    return Response(
                        data={"errors": error_msg},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

        except Exception as e:

            self.message += "".join([".", self.request.__name__, "ERROR => ", str(e)])
            log.error(self.message)
            return Response(
                json.dumps({"errors": self.message}),
                status=status.HTTP_404_NOT_FOUND,
            )
