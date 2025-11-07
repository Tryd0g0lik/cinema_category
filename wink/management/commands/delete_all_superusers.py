"""
# your_app/management/commands/delete_all_users.py
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = "Удаляет всех пользователей (кроме суперпользователей)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--include-superusers",
            action="store_true",
            help="Включить удаление суперпользователей",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Пропустить подтверждение",
        )

    def handle(self, *args, **options):
        include_superusers = options["include_superusers"]
        force = options["force"]

        # Filter for users
        if include_superusers:
            users = User.objects.all()
            user_count = users.count()
            message = f"Вы собираетесь удалить ВСЕХ пользователей ({user_count} записей), включая суперпользователей!"
        else:
            users = User.objects.filter(is_superuser=False)
            user_count = users.count()
            message = f"Вы собираетесь удалить {user_count} пользователей (кроме суперпользователей)!"

        if not force:
            confirm = input(f"{message} Продолжить? [y/N]: ")
            if confirm.lower() != "y":
                self.stdout.write(self.style.WARNING("Отменено"))
                return

        # Drop the users and transactions
        with transaction.atomic():
            deleted_count, _ = users.delete()

        self.stdout.write(
            self.style.SUCCESS(f"Успешно удалено {deleted_count} пользователей")
        )
