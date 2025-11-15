from django.apps import AppConfig


class WinkConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "wink"

    def ready(self):
        from wink.receivers import file_upload_receiver
        from wink.receivers import user_comment_receiver
        from wink.signals import file_upload_signal, user_comment_signal

        user_comment_signal.connect(
            user_comment_receiver, dispatch_uid="record_user_comment"
        )
        file_upload_signal.connect(
            file_upload_receiver, dispatch_uid="task_on_upload_file"
        )
