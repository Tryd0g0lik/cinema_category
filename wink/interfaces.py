"""
wink/interfaces.py

This file is the analogue for 'interfaces.ts' of file from Typescript.
"""

from typing import TypedDict, TypeVar
from django.views import View
from adrf.viewsets import ModelViewSet
from adrf.views import APIView


class FileUpload(TypedDict):
    """
    This is type name of data for which the parent element is class 'FilesModel'.
    """

    id: int
    upload: str
    name: str
    size: int


class Intermediate(TypedDict):
    """
    This is type of date whose paren is the 'IntermediateFilesModel' class.
    """

    id: int
    upload: int
    user: int
    refer: str
    created_at: str
    updated_at: str


# wink/wink_api/upload_files.py
A = TypeVar("A", bound=View)
B = TypeVar("B", bound=APIView)
C = TypeVar("C", bound=ModelViewSet)
