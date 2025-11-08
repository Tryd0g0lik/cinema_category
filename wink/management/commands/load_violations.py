"""
wink/management/commands/load_violations.py
"""

import os
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "load initial violations from file"

    def handle(self, *args, **kwargs):
        from pandas import read_excel as pd_exel
        from django.db import transaction
        from wink.models_wink.violations import BasisViolation

        try:
            file_path = os.path.join(
                settings.BASE_DIR, "media", "classification_events.xlsx"
            )
            df = pd_exel(file_path)
            dF_new = df.rename(
                columns={
                    "Unnamed: 1": "violations",
                    "Unnamed: 2": "context",
                    "Unnamed: 3": "age",
                }
            )
            violations = dF_new["violations"]
            context = dF_new["context"]
            age = dF_new["age"]
            new_context = []
            for i in range(len(violations)):
                new_context.append(f"{age[i]} {violations[i]}")
            basis_violation = []
            [
                basis_violation.append(
                    BasisViolation(
                        violations=context[i], violations_comment=new_context[i]
                    )
                )
                for i in range(len(context))
            ]
            with transaction.atomic():
                BasisViolation.objects.bulk_create(basis_violation)

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error: {e}"))
