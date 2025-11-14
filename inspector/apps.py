"""
App configuration for the inspector app.

This file defines the InspectorConfig class, which registers the app
with Django. Having a separate app allows the API endpoints and
related services to be encapsulated cleanly.
"""
from __future__ import annotations

from django.apps import AppConfig


class InspectorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inspector'
    verbose_name = 'Data Inspector'