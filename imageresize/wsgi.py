"""
WSGI config for imageresize project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "imageresize.settings.local")

application = get_wsgi_application()

# wraps djangos normal wsgi application in whitenose
from whitenoise.django import DjangoWhiteNoise
application = DjangoWhiteNoise(application)
