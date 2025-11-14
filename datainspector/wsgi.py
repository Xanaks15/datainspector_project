"""
WSGI config for datainspector project.

This exposes the WSGI callable as a module-level variable named
``application`` so that it can be used by any WSGI server, such as
Gunicorn or uWSGI. It also configures Django to use the settings
module specified in the DJANGO_SETTINGS_MODULE environment variable.
"""
from __future__ import annotations

import os

from django.core.wsgi import get_wsgi_application  # type: ignore


# Set the default Django settings module for the 'datainspector' project
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'datainspector.settings')

# Get the WSGI application object
application = get_wsgi_application()