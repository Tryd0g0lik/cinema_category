"""
wink/tasks/task_record_user_comment.py
"""

import time
import logging
from django.apps import apps

# # from celery import Celery
# from django.db.models.signals import m2m_changed
from django.core.signals import request_finished
from logs import configure_logging


log = logging.getLogger(__name__)
configure_logging(logging.INFO)

Comments = apps.get_model("wink", "Comments")
IntermediateViolationsComment = apps.get_model("wink", "IntermediateViolationsComment")
IntermediateFilesModel = apps.get_model("wink", "IntermediateFilesModel")


def record_user_comment(sender, **kwargs):
    """
    description: Here, we work with user comments - they, was sent to the AI parser process.
    - kwargs["user_id"] is the user id who sent the comment from web-page.
    - kwargs["comment"] it's the user comment.
    # - kwargs["target_audience"] is the target audience of the film script.
    - kwargs["file_id"] is the file id of the film script.
    :param sender:
    :param kwargs:
    :return:
    """
    user_id = kwargs["user_id"]
    comment = kwargs["comment"]
    # target_audience = kwargs["target_audience"]
    file_id = kwargs["file_id"]
    if not user_id or not comment or not file_id:
        return

    intermediate_file = IntermediateFilesModel.objects.get(pk=file_id)
    refer = intermediate_file.refer
    # ---------- COMMENT ----------
    try:
        comments = Comments(refer=refer, comment=comment)
        comments.save()
        log.info(
            "[%s]: Comment recorded for user %s: %s",
            (record_user_comment.__name__, user_id, comment[:15]),
        )
    except Exception as e:
        log.error(
            "[%s]:  for user %s Error =>  %s",
            (record_user_comment.__name__, user_id, e.args[0]),
        )
        return

    # -----------------------------
    # ---------- COMMENT ----------
    return


request_finished.connect(record_user_comment)
