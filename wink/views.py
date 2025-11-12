"""
flow/views.py
"""

import json
import os
from datetime import time

from django.http import StreamingHttpResponse

from django.shortcuts import render
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.request import Request
from rest_framework.decorators import api_view
from project.settings import BASE_DIR
from wink.models_wink.files import IntermediateFilesModel


# Create your views here.


@api_view(["GET"])
def file_event_stream(request: Request, file_id: int) -> StreamingHttpResponse:

    def event_stream():
        file_obj_lisd = IntermediateFilesModel.objects.filter(upload=file_id)
        if not file_obj_lisd.exists():
            yield f"data: {json.dumps({'status': 'error'})}\n\n"
        # ---------- CYCLE AT THE PROCESS ----------
        while file_obj_lisd[0].status_file == "processing":
            yield f"data: {json.dumps({'status': 'processing'})}\n\n"
            file_obj_lisd[0].refresh_from_db()

        # ---------- READY SUCCESSFUL --------------
        if file_obj_lisd[0].status_file.startswith("ready"):
            yield f"data: {json.dumps({
                'status': file_obj_lisd[0].status_file,
                'download_url': f"/api/v1/wink/download/{file_obj_lisd[0].upload_ai.refer}",
            })}\n\n"
        # ---------- FILE RECEIVED THE ERROR ------
        if file_obj_lisd[0].status_file.startswith("error"):
            yield f"data: {json.dumps({
                'status': file_obj_lisd[0].status_file,
            })}\n\n"

        response = StreamingHttpResponse(
            event_stream(), content_type="text/event-stream"
        )
        response["Cache-Control"] = "no-cache"
        return response


# 3. Server-Sent Events (SSE)


def main(request):

    # GET JS FILES FOR LOGIN AND REGISTER PAGES
    # if "login" in request.path.lower() or "register" in request.path.lower():
    files = os.listdir(f"{BASE_DIR}/collectstatic/scripts")
    files = ["scripts/" + file for file in files]
    return render(request, "index.html", {"js_files": files})
