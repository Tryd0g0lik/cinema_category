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


class Comments(Quantity):
    comment_recommendation = (
        models.TextField(
            null=True,
            blank=True,
            help_text=_("Recommendation comment of AI"),
            verbose_name=_("Recommend"),
            db_column="recommend",
            validators=[],
        ),
    )
    violations = models.ManyToManyField(
        "BasisViolation",
        blank=True,
        verbose_name=_("Violations"),
        db_column="violations",
        help_text=_("Violations - the views of violations"),
    )

    rating = models.CharField(
        default=COMPLIANCE_LEVEL_RATING_CHOICES[0],
        choices=COMPLIANCE_LEVEL_RATING_CHOICES,
        max_length=100,
        verbose_name=_("Rating"),
        db_column="rating",
        help_text=_("Rating from violations"),
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100),
        ],
    )
    target_audience = models.CharField(
        default=AGE_RATING_CHOICES[1],
        choices=AGE_RATING_CHOICES,
        max_length=100,
        help_text=_("Target audience of your document"),
        verbose_name=_("Target Audience"),
        db_column="target_audience",
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100),
        ],
    )
    author = models.ForeignKey(
        "IntermediateFilesModel",
        on_delete=models.CASCADE,
        verbose_name=_("Author"),
        db_column="author",
        related_name="comments",
        help_text=_("Who is uploading the document"),
    )
    reference_file = CharField(
        null=True,
        blank=True,
        max_length=100,
        verbose_name=_("Reference File"),
        db_column="reference_file",
        help_text=_("Reference File - it's the pathname of file inside the server"),
    )
    refer_file = models.OneToOneField(
        "IntermediateFilesModel",
        unique=True,
        to_field="refer",
        on_delete=models.CASCADE,
        verbose_name=_("Reference File"),
        db_column="refer_file_uuid_id",
        related_name="refers",
    )
