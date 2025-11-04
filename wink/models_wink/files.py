"""
wink/models_wink/files.py
"""

import datetime
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import (
    FileExtensionValidator,
    MinValueValidator,
    MaxLengthValidator,
    RegexValidator,
    MaxValueValidator,
)
from django.contrib.auth.models import User

# from project.settings import WAGTAILDOCS_EXTENSIONS


class FilesModel(models.Model):
    upload = models.FileField(
        upload_to="files/%Y/%m/%d/",
        db_column="file",
        help_text=_("Upload the file - pdf, docx"),
        verbose_name=_("File"),
        # validators=[FileExtensionValidator(allowed_extensions=WAGTAILDOCS_EXTENSIONS)],
    )

    class Meta:
        verbose_name = _("File")
        verbose_name_plural = _("Files")
        db_table = "files"

    def __str__(self):
        return self.upload.name

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)

class IntermediateFilesModel(models.Model):
    upload = models.ForeignKey(
        FilesModel,
        on_delete=models.CASCADE,
        verbose_name=_("File"),
        db_column="file_id",
        help_text=_("Select existing the file id"),
        related_name="loaded_files",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("User"),
        db_column="user_id",
        help_text=_("Select the user id"),
        related_name="loaded_files",
    )
    created_at = (
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
    )
    updated_at = (
        models.DateField(
            auto_now=True,
            verbose_name=_("Updated at"),
            help_text=_("Past time when the file was updated"),
            db_column="updated_at",
        ),
    )

    refer = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        verbose_name=_("Reference"),
        editable=False,
        db_column="refer",
        help_text=_("Reference link to the file - pdf, docx"),
    )

    class Meta:
        verbose_name = _("Intermediate_files")
        verbose_name_plural = _("Intermediate_files")
        db_table = "intermediate_files"


    def __str__(self):
        return f" File Id: {self.upload} was created at {self.created_at}."
