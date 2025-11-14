"""
URL configuration for the inspector app.

Routes API endpoints to views. Each URL pattern corresponds to one
analysis endpoint described in the requirements. The patterns are
prefixed with `/api/` at the project level in datainspector/urls.py.
"""
from __future__ import annotations

from django.urls import path

from .views import (
    DatasetList,
    SummaryView,
    MissingView,
    DtypesView,
    NuniqueView,
    OutlierView,
    DuplicatesView,
    ColumnsView,
)


urlpatterns = [
    # List datasets or upload a new one
    path('datasets/', DatasetList.as_view(), name='dataset-list'),
    # Summary statistics for a dataset
    path('datasets/<str:dataset_id>/summary/', SummaryView.as_view(), name='dataset-summary'),
    # Missing values by column
    path('datasets/<str:dataset_id>/missing/', MissingView.as_view(), name='dataset-missing'),
    # Data types by column
    path('datasets/<str:dataset_id>/dtypes/', DtypesView.as_view(), name='dataset-dtypes'),
    # Number of unique values by column
    path('datasets/<str:dataset_id>/nunique/', NuniqueView.as_view(), name='dataset-nunique'),
 
    path("datasets/<str:dataset_id>/outliers/", OutlierView.as_view()),

    # Duplicate rows sample and count
    path('datasets/<str:dataset_id>/duplicates/', DuplicatesView.as_view(), name='dataset-duplicates'),
    # List of columns
    path('datasets/<str:dataset_id>/columns/', ColumnsView.as_view(), name='dataset-columns'),
]