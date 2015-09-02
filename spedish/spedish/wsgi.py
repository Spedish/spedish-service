"""
WSGI config for spedish project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os,sys

sys.path.append('/var/spedish_site/spedish/spedish')
sys.path.append('/var/spedish_site/spedish/')

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spedish.settings")

application = get_wsgi_application()
