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

CommentsModel = apps.get_model("wink", "CommentsModel")
IntermediateCommentModel = apps.get_model("wink", "IntermediateCommentModel")
IntermediateFilesModel = apps.get_model("wink", "IntermediateFilesModel")


def record_user_comment(sender, **kwargs):
    """
    Если на входе указали:
     1) author = "User": просто сохраняем в таблице "Comment".
     2) author = "AI":
        2.1) Смотрим - оставлял пользователь комментарии раньше или нет. Если не оставлял , то переменая 'user_last_comment_id'имеет None.
        Иначе из последнего комментария получаем объект/образ комментария. !! Всегда из последенего комменатрия от пользователя.
    description: Here, we work with user comments - they, was sent to the AI parser process.
    - kwargs["user_id"] is the user id who sent the comment from web-page.
    - kwargs["comment"] it's the user comment.
    # - kwargs["target_audience"] is the target audience of the film script.
    - kwargs["author"] is  the 'AI' or 'User'
    - kwargs["file_id"] is the file id of the film script.
    :param sender:
    :param kwargs:
    :return:
    """
    user_id = kwargs["user_id"]
    comment = kwargs["comment"]
    # target_audience = kwargs["target_audience"]
    file_id = kwargs["file_id"]

    author = kwargs["author"]
    if not user_id or not comment or not file_id:
        return

    intermediate_file = IntermediateFilesModel.objects.get(pk=file_id)
    refer = intermediate_file.refer
    # ---------- COMMENT ----------
    if author.lower() == "User".lower():
        # If the author == 'User'
        try:
            comments_user = CommentsModel(refer=refer, comment=comment, author=author)
            comments_user.save()
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
    else:
        # If the author == 'AI'
        user_last_comment_list = IntermediateCommentModel.objects.filter(
            refer=refer, author="User"
        )
        user_last_comment = (
            user_last_comment_list[-1] if len(user_last_comment_list) > 0 else None
        )
        comment_ai = CommentsModel(refer=refer, comment=comment, author=author)
        comment_ai.save()
        if not user_last_comment:
            user_last_comment = None

        inntermediate_comments = IntermediateCommentModel(
            comments_user=user_last_comment, comments_ai=comment_ai, refer=refer
        )
        inntermediate_comments.save()
    # -----------------------------
    # ---------- COMMENT ----------
    return


request_finished.connect(record_user_comment)
