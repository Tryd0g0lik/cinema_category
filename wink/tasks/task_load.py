import asyncio
import logging

import requests

from logs import configure_logging
from project.settings import APP_PROTOCOL, APP_HOST, APP_PORT
from wink.winkClient import AsyncHttpClient, HttpRequest

log = logging.getLogger(__name__)
configure_logging(logging.INFO)


async def task_on_upload_file(sender, **kwargs):
    """
    Here we want to upload the file
    :param str kwargs["refer"]: this is the key to the file.
    :return:
    """
    print("Start the signal by the AI & upload file")
    message = "[%s]:" % task_on_upload_file.__name__
    log.info("%s Received notification" % message)
    refer = kwargs["refer"]
    if not refer or not isinstance(refer, str) or len(refer.strip()) == 0:
        t = "[%s]: Error => kwargs did not received" % message
        print(t)
        log.error(t)
        return

    client = AsyncHttpClient()
    response = await client.request(
        HttpRequest.GET.value,
        f"{APP_PROTOCOL}://{APP_HOST}:{APP_PORT}/api/v1/wink/download/{refer}/",
    )
    t = "[%s]: IS ALL SUCCESSFUL. Status code: %s " % (message, response.status_code)
    if response.status_code >= 400:
        t = "[%s]: IS NOT ALL SUCCESSFUL. Status code: %s " % (
            message,
            response.status_code,
        )
    else:
        ref = response.data

        print("========= YOUR FILE ===")
        print(response.data)
        print("==================")
    log.info(t)
