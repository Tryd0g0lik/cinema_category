"""
wink/receivers.py
"""

import asyncio
import logging
from logs import configure_logging
from wink.tasks.task_record_user_comment import record_user_comment
from wink.tasks.task_load import task_on_upload_file

log = logging.getLogger(__name__)
configure_logging(logging.INFO)


def user_comment_receiver(sender, **kwargs):
    """
    This is the Listener of event bo comment from the 'wink.wink_api.files.views_intermediate_files_api.IntermediateFilesViewSet.create'
    :param sender:
    :param kwargs:
    :return:
    """
    try:
        record_user_comment(sender, **kwargs)
    except Exception:
        import logging

        log.error("Error in user_comment_receiver")


def file_upload_receiver(sender, **kwargs):
    """
    This is the Listener of event bo comment from the 'wink.wink_api.files.views_intermediate_files_api.IntermediateFilesViewSet.create'
    :param sender:
    :param kwargs:
    :return:
    """
    try:
        asyncio.create_task(task_on_upload_file(sender, **kwargs))
    except Exception:
        log.error("Error in file_upload_receiver")
