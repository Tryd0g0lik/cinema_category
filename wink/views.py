"""
flow/views.py
"""

import os

from django.shortcuts import render

from project import settings
from project.settings import BASE_DIR


# Create your views here.


def main(request):

    # GET JS FILES FOR LOGIN AND REGISTER PAGES
    # if "login" in request.path.lower() or "register" in request.path.lower():
    files = os.listdir(f"{BASE_DIR}/collectstatic/scripts")
    files = ["scripts/" + file for file in files]
    return render(request, "index.html", {"js_files": files})
