import datetime

from django.db import models
from django.core.validators import (
    MinValueValidator,
    RegexValidator,
    MinLengthValidator,
)
from django.db.models import ForeignKey, CharField

# from pygments.styles.dracula import comment

from project.settings import (
    COMPLIANCE_LEVEL_RATING_CHOICES,
    AUTHOR_OF_COMMET,
)
from django.utils.translation import gettext_lazy as _

from wink.models_wink.violations import Quantity


class CommentsModel(models.Model):
    """
    Коменты от юзера, когда он отправляет данные из формы на анализ.
    Сохраняем комментарий пользоватя.
    Когда пройдёт время и файл будет проанализирован - рекомендационный комментарий  сохраним в IntermediateViolationsComment.
    """

    comment = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Comments"),
    )
    refer_file = models.OneToOneField(
        "IntermediateFilesModel",
        on_delete=models.CASCADE,
        to_field="refer",
        db_column="refer_file",
        related_name="refer_files",
        verbose_name=_("Reference File"),
        help_text=_("Reference link to the file - pdf, docx"),
    )

    comment_author = models.CharField(
        default="User",
        choices=AUTHOR_OF_COMMET,
        help_text=_("Comment author is AI  or User."),
        verbose_name=_("Comment author"),
        validators=[
            MinLengthValidator(2),
            RegexValidator(
                regex=r"(^[A-Z][A-Za-z-_]+$)",
            ),
        ],
    )

    created_at = models.DateField(
        blank=True,
        null=True,
        default=datetime.date.today().strftime("%Y-%m-%d"),
        verbose_name=_("Created at"),
        help_text=_("Created at"),
        db_column="created_at",
        validators=[],
    )

    updated_at = models.DateField(
        auto_now=True,
        verbose_name=_("Updated at"),
        help_text=_("Past time when the file was updated"),
        db_column="updated_at",
    )

    class Meta:
        verbose_name = _("Comments")
        verbose_name_plural = _("Comments")
        db_table = "wink_comments"
        ordering = ["id"]

    def __str__(self):
        return f"Entry made: {self.comment_author} by refer: {self.refer} - {self.created_at}"


class IntermediateCommentModel(Quantity):
    """
    Таблица связанная с AI,
    Рекомендации от AI
    Заполняется при наличии Рекомендаций от AI
    От AI в обратку приходит рефер.
    По реферу определяет комент ползователя к реккмендации к файлу
    По реферу определяет комент ползователя к комент от файла
    Комент из  таблици - Comments
    """

    comments_user = models.ForeignKey(
        "CommentsModel",
        on_delete=models.CASCADE,
        verbose_name=_("Comments of user"),
        db_column="comments_user",
        related_name="comments_user",
        null=True,
        blank=True,
    )
    rating = models.CharField(
        default="----",
        choices=COMPLIANCE_LEVEL_RATING_CHOICES,  # рейтинг AI который указал AI
        verbose_name=_("Rating"),
        help_text=_("Rating from violations"),
        validators=[
            MinValueValidator(1),
        ],
        null=True,
        blank=True,
    )
    refer = models.OneToOneField(
        "IntermediateFilesModel",
        on_delete=models.CASCADE,
        to_field="refer",
        # editable=False,  # По этому ключу можем искать комент пользователя в "Comments"
        db_column="refer",
        related_name="comment_inter",
        max_length=50,
        help_text=_("Reference link to the file - pdf, docx"),
    )
    created_at = models.DateField(
        blank=True,
        null=True,
        default=datetime.date.today().strftime("%Y-%m-%d"),
        verbose_name=_("Created at"),
        help_text=_("Created at"),
        db_column="created_at",
        validators=[],
    )
    updated_at = models.DateField(
        auto_now=True,
        verbose_name=_("Updated at"),
        help_text=_("Past time when the file was updated"),
        db_column="updated_at",
    )

    class Meta:
        verbose_name = _("Response AI")
        verbose_name_plural = _("Response AI")

    def __str__(self):
        return f"Intermediate Comment {str(self.comments_user)} - {self.refer}"
