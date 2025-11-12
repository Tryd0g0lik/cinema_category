"""
wink/models_wink/files.py
"""

import datetime
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import (
    MinValueValidator,
    RegexValidator,
    MaxValueValidator,
)
from django.contrib.auth.models import User

from project.settings import AGE_RATING_CHOICES, STATUS_FILE
from wink.models_wink.comments import Quantity


class FilesModel(models.Model):
    """
    Сюда получаем файл
    Доступный всем пользователям
    :param: str upload: is local path of the file. This is the file sent to the server (AI parsing)
    :param: str name: is the file name.
    :param: str size: is the file size.
    """

    upload = models.FileField(
        upload_to="upload/%Y/%m/%d/",
        help_text=_("Upload the file - pdf, docx, json"),
        verbose_name=_("File"),
        null=True,
        blank=True,
        # validators=[FileExtensionValidator(allowed_extensions=WAGTAILDOCS_EXTENSIONS)]
    )
    name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
    )
    size = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0),
        ],
    )

    class Meta:
        verbose_name = _("File")
        verbose_name_plural = _("Files")
        db_table = "wink_files"

    def __str__(self):
        return self.upload.name

    def save(self, *args, **kwargs):
        if self.upload:
            self.name = self.upload.name.split("/")[-1]
            self.size = self.upload.size
        return super().save(*args, **kwargs)


class IntermediateFilesModel(Quantity):
    """ "
    отправляем файл на анализ
    АШ скачивает файл
    по запросу запускаем задали celery и делаем рефер
    :param int upload: is index of file which was sent to the server.
    :param int user: is index of user (after authentication).
    :param str target_audience: is target audience for the film script/scenario.
    :param str refer: is the refer key for the film script. It's unique - here.
    :param str created_at: is date when the file was created.
    :param str updated_at: is date when the file was updated.
    """

    upload = models.ForeignKey(
        FilesModel,
        on_delete=models.CASCADE,
        verbose_name=_("File"),
        db_column="file_id",
        help_text=_("Select existing the file id"),
        related_name="loaded_files",
    )
    upload_ai = models.OneToOneField(
        FilesModel,
        on_delete=models.CASCADE,
        verbose_name=_("File"),
        db_column="file_ai",
        help_text=_("Select existing the file id - This is the result of the analysis"),
        related_name="analysis_files",
        null=True,
        blank=True,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("User"),
        db_column="user_id",
        help_text=_("Select the user id"),
        related_name="loaded_files",
    )
    violations = models.ManyToManyField(
        "BasisViolation",
        blank=True,
        verbose_name=_("Violations"),
        db_column="violations",
        help_text=_("Violations - the views of violations"),
    )
    target_audience = models.CharField(
        default=AGE_RATING_CHOICES[1],
        choices=AGE_RATING_CHOICES,
        max_length=5,  # юзер указывает целевую аудиторию документа перед отправкой на анализ
        help_text=_("Target audience for the film script"),
        verbose_name=_("Target Audience"),
        db_column="target_audience",
        validators=[
            MinValueValidator(2),
            MaxValueValidator(5),
            RegexValidator(
                regex=r"(^\d+\+$)",
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
        validators=[
            # RegexValidator(regex="(^\d{4}-\d{2}-\d{2}$)"),
        ],
    )

    updated_at = models.DateField(
        auto_now=True,
        verbose_name=_("Updated at"),
        help_text=_("Past time when the file was updated"),
        db_column="updated_at",
    )

    refer = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        verbose_name=_("Reference"),
        editable=False,
        db_column="refer",
        max_length=50,
        help_text=_("Reference link to the file - pdf, docx"),
    )
    status_file = models.CharField(
        default=STATUS_FILE[0],
        choices=STATUS_FILE,
        max_length=20,
        help_text=_("Status of the file to be parsing"),
        verbose_name=_("Status"),
        db_column="status_file",
    )

    class Meta:
        verbose_name = _("Intermediate_files")
        verbose_name_plural = _("Intermediate_files")
        db_table = "wink_intermediate_files"

    def __str__(self):
        return f" File Id: {self.upload} was created at {self.created_at}."
