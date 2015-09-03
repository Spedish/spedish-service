"""
Template for local settings

Your local settings file should not be checked in
"""

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '<database name>',
        'USER': '<user>',
        'PASSWORD': '<pass>',
        'HOST': '<hostname>',
        'PORT': '3306',
    }
}

