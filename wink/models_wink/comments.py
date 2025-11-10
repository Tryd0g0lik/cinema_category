import datetime

from django.db import models
from django.core.validators import (
    FileExtensionValidator,
    MinValueValidator,
    MaxLengthValidator,
    RegexValidator,
    MaxValueValidator,
)
from django.db.models import ForeignKey, CharField

# from pygments.styles.dracula import comment

from project.settings import (
    AGE_RATING_CHOICES,
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
    refer = models.OneToOneField(
        # """"
        # Комментарий от пользователя указываем ДО отправления на анализ или
        # после?
        # """
        "IntermediateFilesModel",
        unique=True,  # реферальный клююч. Вероятно его забираем из поступившего анализа
        # ключ создаём при отправке файла на анализ.
        to_field="refer",
        on_delete=models.CASCADE,
        verbose_name=_("Reference File"),
        db_column="refer_file_uuid_id",
        related_name="refers",
    )
    comment_author = models.CharField(
        default=AUTHOR_OF_COMMET[1],
        choices=AUTHOR_OF_COMMET,
        max_length=30,
        help_text=_("Comment author is AI  or User."),
        verbose_name=_("Comment author"),
        validators=[
            MinValueValidator(2),
            MaxValueValidator(30),
            RegexValidator(
                regex=r"(^[A-Z][A-Za-z-_]+$)",
            ),
        ],
    )

    created_at = (
        (
            models.DateField(
                blank=True,
                null=True,
                default=datetime.datetime.now,
                verbose_name=_("Created at"),
                help_text=_("Created at"),
                db_column="created_at",
                validators=[],
            ),
        ),
    )
    updated_at = (
        models.DateField(
            auto_now=True,
            verbose_name=_("Updated at"),
            help_text=_("Past time when the file was updated"),
            db_column="updated_at",
        ),
    )

    class Meta:
        verbose_name = _("Comments")
        verbose_name_plural = _("Comments")
        db_table = "wink_comments"
        ordering = ["id"]


class IntermediateCommentModel(Quantity):
    """
    Таблица связанная с AI,
    Рекомендации от AI
    Заполняется при наличии Рекомендаций от AI
    От AI в обратку приходит рефер.
    По реферу определяет комент ползователя к реккмендации к файлу
    По реферу определяет комент ползователя к комент от файла
    Комент и рекомендационный комментарий из одной таблици - Comments
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
    comments_ai = models.ForeignKey(
        "CommentsModel",
        on_delete=models.CASCADE,
        verbose_name=_("Comments of user"),
        db_column="comments_ai",
        related_name="comments_ai",
        help_text=_("Recommendation comment of AI"),
    )
    rating = models.CharField(
        default=COMPLIANCE_LEVEL_RATING_CHOICES[0],
        choices=COMPLIANCE_LEVEL_RATING_CHOICES,
        max_length=100,  # рейтинг AI который указал AI
        verbose_name=_("Rating"),
        help_text=_("Rating from violations"),
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100),
        ],
        null=True,
        blank=True,
    )
    refer = models.CharField(
        # " ключ получаем из  поступивших результатов анализа от AI
        verbose_name=_("Reference"),
        editable=False,  # По этому ключу можем искать комент пользователя в "Comments"
        db_column="refer",
        unique=True,
        max_length=50,
        help_text=_("Reference link to the file - pdf, docx"),
    )
    created_at = (
        (
            models.DateField(
                blank=True,
                null=True,
                default=datetime.datetime.now,
                verbose_name=_("Created at"),
                help_text=_("Created at"),
                db_column="created_at",
                validators=[
                    # RegexValidator(regex="(^\d{4}-\d{2}-\d{2}$)"),
                ],
            ),
        ),
    )
    updated_at = (
        models.DateField(
            auto_now=True,
            verbose_name=_("Updated at"),
            help_text=_("Past time when the file was updated"),
            db_column="updated_at",
        ),
    )

    class Meta:
        verbose_name = _("Comment is intermediate")
        verbose_name_plural = _("Comments is intermediates")
        # db_table = "wink_comments_intermediate"

    def __str__(self):
        return f"Рекомендация: {self.comments_ai}"

    # def save(self, *args, **kwargs):
    #     """
    #
    #     :param args:
    #     :param kwargs:
    #     :return:
    #     """
    #     # comment_user = Comments.objects
    #     comment = self.comments_user.objects.filter(refer=self.refer)
    #
    #     if self.comments_user and len(comment) > 0:
    #         comment
    #         self.comments_user = comment.first()
    #
    #     super().save(*args, **kwargs)
