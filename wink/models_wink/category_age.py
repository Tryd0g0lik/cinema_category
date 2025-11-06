from django.core.validators import FileExtensionValidator
from django.db import models
from django.core.validators import (
    FileExtensionValidator,
    MinValueValidator,
    MaxLengthValidator,
    RegexValidator,
    MaxValueValidator,
)
from project.settings import AGE_RATING_CHOICES
from django.utils.translation import gettext_lazy as _


class AgeCategory(models.Model):
    age_category = models.CharField(
        default=AGE_RATING_CHOICES[1],
        choices=AGE_RATING_CHOICES,
    )


class Comments(models.Model):
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
    rating = models.CharField()
    author = (
        models.ForeignKey(
            "IntermediateFilesModel",
            on_delete=models.CASCADE,
            verbose_name=_("Author"),
            db_column="author",
            related_name="comments",
            help_text=_("Index of user"),
        ),
    )
