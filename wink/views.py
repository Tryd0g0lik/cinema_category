"""
flow/views.py
"""

import json
import os
from django.http import StreamingHttpResponse
from django.apps import apps
from django.shortcuts import render
from rest_framework.request import Request

from project import settings
from project.settings import BASE_DIR

IntermediateFilesModel = apps.get_model("wink", "IntermediateFilesModel")

# Create your views here.


def file_event_stream(request: Request, **kwargs) -> StreamingHttpResponse:
    refer = kwargs["refer"].strip()

    def event_stream():
        file_obj = IntermediateFilesModel.object.filter(refer=refer)
        if not file_obj.exists():
            pass


# 3. Server-Sent Events (SSE)


def main(request):

    # GET JS FILES FOR LOGIN AND REGISTER PAGES
    # if "login" in request.path.lower() or "register" in request.path.lower():
    files = os.listdir(f"{BASE_DIR}/collectstatic/scripts")
    files = ["scripts/" + file for file in files]
    return render(request, "index.html", {"js_files": files})
