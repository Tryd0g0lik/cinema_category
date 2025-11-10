from django.db import models
from django.core.validators import (
    MinValueValidator,
    RegexValidator,
    MaxValueValidator,
)
from django.utils.translation import gettext_lazy as _


class Quantity(models.Model):
    violations_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Violations Quantity"),
    )

    class Meta:
        abstract = True


class BasisViolation(models.Model):
    """
    насилие, ненормативная лексика, эротический контент, алкоголь/наркотики, пугающие сцены,  сигареты
    NODE: добавить авто загрузку базово списка из файла.
    """

    violations = models.CharField(
        max_length=50,
        verbose_name=_("Violations"),
        db_column="violations",
        help_text=_("Violations - the views of violations"),
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100),
            RegexValidator(
                regex=r"^[A-Za-z- ,]+$",
            ),
        ],
    )

    violations_comment = models.CharField(
        max_length=100,
        verbose_name=_("Violations_comments"),
        db_column="violations_comment",
        help_text=_("Example - Нецензурная лексика - Мат, обсценная речь 16+ / 18+"),
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100),
            RegexValidator(
                regex=r"^[A-Za-z- +/0-9]+$",
            ),
        ],
    )

    class Meta:
        verbose_name = _("Basis Violation")
        verbose_name_plural = _("Basis Violations")
        db_table = "wink_violations"
