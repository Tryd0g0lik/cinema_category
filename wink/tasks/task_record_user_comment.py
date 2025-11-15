"""
wink/tasks/task_record_user_comment.py
"""

import time
import logging
from django.apps import apps
from logs import configure_logging


log = logging.getLogger(__name__)
configure_logging(logging.INFO)

CommentsModel = apps.get_model("wink", "CommentsModel")
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
    print("Start the signal by the user commit")
    log.info(
        "[%s]: Start the signal by the user commit",
        (record_user_comment.__name__,),
    )
    user_id = kwargs["user_id"]
    comment = kwargs["comment"]
    file_id = kwargs["file_id"]
    author = kwargs["author"]
    if not user_id or not comment or not file_id or author.lower() == "User".lower():
        return

    intermediate_file = IntermediateFilesModel.objects.get(pk=file_id)
    refer = intermediate_file.refer
    # ---------- COMMENT FROM USER-
    try:
        comments_user = CommentsModel(refer_file=refer, comment=comment, author=author)
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
