# middleware/error_handling.py
import logging
from django.http import JsonResponse, Http404

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):

        if isinstance(exception, Http404):
            return JsonResponse(
                {
                    "error": "Not Found",
                    "message": "The requested resource was not found",
                    "path": request.path,
                },
                status=404,
            )

        logger.error(f"Server error: {exception}", exc_info=True)
        return JsonResponse(
            {
                "error": "Internal Server Error",
                "message": "An unexpected error occurred",
            },
            status=500,
        )
