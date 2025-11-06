import logging
from django.contrib.auth.models import User
from django.db import OperationalError, DatabaseError


from logs import configure_logging


log = logging.getLogger(__name__)
configure_logging(logging.INFO)
class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self._root_user_initialized = False
        self._root_user = None

    def __call__(self, request):
        # Инициализируем root user только один раз при первом успешном подключении к БД
        if not self._root_user_initialized:
            self._initialize_root_user()

        if self._root_user:
            request.user = self._root_user

        response = self.get_response(request)
        return response

    def _initialize_root_user(self):
        """Инициализировать root пользователя один раз при старте приложения"""
        try:
            self._root_user = User.objects.get(username="root")
            log.info("Root user found in database")
            self._root_user_initialized = True
        except User.DoesNotExist:
            try:
                self._root_user = User.objects.create_user(
                    username="root",
                    email="email@email.ru",
                    password="123"
                )
                self._root_user.is_staff = True
                self._root_user.is_active = True
                self._root_user.save()
                log.info("Root user created successfully")
                self._root_user_initialized = True
            except (OperationalError, DatabaseError) as e:
                log.warning(f"Cannot create root user - database unavailable: {e}")
                self._root_user = None
        except (OperationalError, DatabaseError) as e:
            log.warning(f"Cannot initialize root user - database error: {e}")
            self._root_user = None
