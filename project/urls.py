"""
project/urls.py
"""

from django.contrib import admin
# from wagtail.admin import urls as wagtailadmin_urls
# from wagtail import urls as wagtail_urls
# from wagtail.documents import urls as wagtaildocs_urls
from django.urls import path, include, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny
from django.conf.urls.static import static
from django.views.generic import TemplateView
from project import settings
from project.urls_api import urlpatterns as api_wink
from wink.urls import urlpatterns as urls_wink


schema_view = get_schema_view(
    openapi.Info(
        title="API for WINK Hakaton",
        description="При написании сценария важно придерживаться выбранного возрастного рейтинга, устанавливаемого на основании норм Возрастной классификации информационной продукции. Такой подход гарантирует попадание контента в оптимальные эфирные/кинопрокатные слоты и доступность на стриминговых платформах, что позволяет достичь целевой аудитории зрителей. Автоматическая проверка рейтинга по сценарию позволяет авторам и продюсерам заранее понимать, где текст может выйти за рамки выбранной категории - делая процесс производства быстрее, прозрачнее и экономичнее.",
        default_version="v1",
        service_identity=False,
        contact=openapi.Contact(email="work80@mail.ru"),
    ),
    public=True,
    permission_classes=[AllowAny],
    patterns=[
        path("api/v1/", include((api_wink, "api_v1"), namespace="api_v1")),
    ],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("wink/", include((urls_wink, "wink"), namespace="wink")),
    # path("api/", include((api_wink, "api_keys"), namespace="api_keys")),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="swagger"),
    path(
        "swagger<format>/",
        schema_view.without_ui(cache_timeout=0),
        name="swagger-format",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="redoc"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += [
    # path("cms/", include(wagtailadmin_urls)),
    # path("documents/", include(wagtaildocs_urls)),
    # path("pages/", include(wagtail_urls)),
    re_path(
        r"^(?!static/|media/|api/|admin/|redoc/|swagger/).*",
        TemplateView.as_view(template_name="index.html"),
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
