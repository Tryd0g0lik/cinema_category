from django.db import models
from django.core.validators import (
    FileExtensionValidator,
    MinValueValidator,
    MaxLengthValidator,
    RegexValidator,
    MaxValueValidator,
)
from django.db.models import ForeignKey, CharField

from project.settings import AGE_RATING_CHOICES, COMPLIANCE_LEVEL_RATING_CHOICES
from django.utils.translation import gettext_lazy as _

from wink.models_wink.violations import Quantity


class Comments(models.Model):
    """
    Коменты от юзера
    """

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
    target_audience = models.CharField(
        default=AGE_RATING_CHOICES[1],
        choices=AGE_RATING_CHOICES,
        max_length=100,  # юзер указывает целевую аудиторию документа перед отправкой на анализ
        help_text=_("Target audience of your document"),
        verbose_name=_("Target Audience"),
        db_column="target_audience",
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100),
        ],
    )
    # author = models.ForeignKey(
    #     "IntermediateFilesModel",
    #     on_delete=models.CASCADE,
    #     verbose_name=_("Author"),
    #     db_column="author", # кто отправил документ
    #     related_name="comments",
    #     help_text=_("Who is uploading the document"),
    # )
    reference_file = CharField(
        null=True,  # !!!!???
        blank=True,
        max_length=100,  # локальная ссылка на файл (поступивший из фронта) !! Но есть промежуточная таблица с файлами
        verbose_name=_("Reference File"),
        db_column="reference_file",
        help_text=_("Reference File - it's the pathname of file inside the server"),
    )

    class Meta:
        verbose_name = _("Comments")
        verbose_name_plural = _("Comments")
        db_table = "wink_comments"


class IntermediateViolationsComment(Quantity):
    """
    ТNаблица связанная с AI
    Рекомендации от AI
    От AI в обратку приходит рефер.
    По реферу определяет комент ползователя к данному файлу.реккомендации
    """

    comments_user = models.ForeignKey(
        "Comments",
        on_delete=models.CASCADE,
        verbose_name=_("Comments of user"),
        db_column="comments_user",
        related_name="comments_violations",
    )
    violations = models.ForeignKey(
        "BasisViolation",  # берём классы нарушений и комент к ним (статичный) Как рекоментация от AI
        verbose_name=_("Violations"),
        on_delete=models.CASCADE,
        db_column="violations",  # Какие классы брать - это смотрим в поступивший результат анализа от AI
        help_text=_("Violations - the views of violations"),
        related_name="comments_violations",
    )
    comment_recommendation = (
        models.TextField(
            null=True,  # РеКомендации от AI
            blank=True,
            help_text=_("Recommendation comment of AI"),
            verbose_name=_("Recommend"),
            db_column="recommend",
            validators=[],
        ),
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
