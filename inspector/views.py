"""
API views for the inspector app.

These views implement a lightweight REST API for uploading datasets and
computing various statistics about them. The API is designed to be
stateless: each request reloads and processes the dataset on demand
using pandas. This makes it easy to replace the underlying CSV file
without restarting the server or invalidating cached results.
"""
from __future__ import annotations

import os
import uuid
from typing import Any, Dict, List

from django.conf import settings
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

from .services import DataProfile


def _get_dataset_path(dataset_id: str) -> str:
    """Resolve a dataset ID to its file path in the media directory.

    Looks for a file with a name that starts with the given dataset_id.
    Raises Http404 if no matching file is found.
    """
    media_root = settings.MEDIA_ROOT
    for fname in os.listdir(media_root):
        if fname.startswith(dataset_id):
            return os.path.join(media_root, fname)
    raise Http404(f"Dataset with ID '{dataset_id}' not found")


class DatasetList(APIView):
    """List available datasets or upload a new CSV file."""

    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, format=None) -> Response:  # type: ignore
        """Return a list of datasets currently stored on the server."""
        datasets: List[Dict[str, str]] = []
        for fname in os.listdir(settings.MEDIA_ROOT):
            # Expect filenames in the form of `<uuid>.<ext>`
            dataset_id, _sep, _ext = fname.partition('.')
            datasets.append({
                'id': dataset_id,
                'file_name': fname,
            })
        return Response({'datasets': datasets})

    def post(self, request, format=None) -> Response:  # type: ignore
        """Handle CSV uploads and return the assigned dataset ID."""
        # Ensure a file was provided
        if 'file' not in request.FILES:
            return Response({'detail': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        upload = request.FILES['file']
        # Generate a unique dataset ID using UUID4
        dataset_id = uuid.uuid4().hex
        # Preserve the original file extension
        ext = os.path.splitext(upload.name)[1] or '.csv'
        file_name = f"{dataset_id}{ext}"
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)
        # Save the uploaded file to disk
        with open(file_path, 'wb+') as destination:
            for chunk in upload.chunks():
                destination.write(chunk)
        return Response({'id': dataset_id, 'file_name': upload.name}, status=status.HTTP_201_CREATED)


class SummaryView(APIView):
    """Return basic summary statistics for a dataset."""
    def get(self, request, dataset_id: str, format=None) -> Response:  # type: ignore
        file_path = _get_dataset_path(dataset_id)
        profile = DataProfile(file_path)
        data = profile.summary()
        return Response(data)

class OutlierView(APIView):
    def get(self, request, dataset_id):
        file_path = _get_dataset_path(dataset_id)
        profile = DataProfile(file_path)
        return Response(profile.outlier_table())



class MissingView(APIView):
    """Return missing value counts by column for a dataset."""
    def get(self, request, dataset_id: str, format=None) -> Response:  # type: ignore
        file_path = _get_dataset_path(dataset_id)
        profile = DataProfile(file_path)
        data = profile.missing()
        return Response(data)


class DtypesView(APIView):
    """Return inferred data types for each column of a dataset."""
    def get(self, request, dataset_id: str, format=None) -> Response:  # type: ignore
        file_path = _get_dataset_path(dataset_id)
        profile = DataProfile(file_path)
        data = profile.dtypes()
        return Response(data)


class NuniqueView(APIView):
    """Return the number of unique values for each column of a dataset."""
    def get(self, request, dataset_id: str, format=None) -> Response:  # type: ignore
        file_path = _get_dataset_path(dataset_id)
        profile = DataProfile(file_path)
        data = profile.nunique()
        return Response(data)


class DuplicatesView(APIView):
    """Return duplicate rows and their count for a dataset."""
    def get(self, request, dataset_id: str, format=None) -> Response:  # type: ignore
        file_path = _get_dataset_path(dataset_id)
        profile = DataProfile(file_path)
        data = profile.duplicates()
        return Response(data)


class ColumnsView(APIView):
    """Return a list of column names for a dataset."""
    def get(self, request, dataset_id: str, format=None) -> Response:  # type: ignore
        file_path = _get_dataset_path(dataset_id)
        profile = DataProfile(file_path)
        data = profile.columns()
        return Response(data)