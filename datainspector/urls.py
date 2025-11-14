"""
URL configuration for the datainspector project.

This module routes incoming HTTP requests to the appropriate views. It
includes the inspector API URLs under the `/api/` path and serves the
single-page dashboard at the root URL using a TemplateView.
"""
from __future__ import annotations

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView


urlpatterns = [
    path('admin/', admin.site.urls),
    # Include the inspector app's API routes under the `/api/` prefix
    path('api/', include('inspector.urls')),
    # Serve the dashboard from the root URL
    path('', TemplateView.as_view(template_name='index.html'), name='dashboard'),
]