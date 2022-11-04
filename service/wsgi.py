"""
WSGI config for wavu project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os
import sys
import django
import config
from django.core.wsgi import get_wsgi_application

path = "/mnt/c/Users/facub/Documents/GitHub/wavU"
if path not in sys.path:
    sys.path.insert(0, path)

os.environ["DJANGO_SETTINGS_MODULE"] = 'service.settings.production'
django.setup()
application = get_wsgi_application()
