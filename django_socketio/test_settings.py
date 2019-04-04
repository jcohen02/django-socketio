
from django.conf import settings

SECRET_KEY = 'testing-key'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'django_socketio_tests.db',
    }
}

ROOT_URLCONF = 'django_socketio.urls'

HOST = getattr(settings, "SOCKETIO_HOST", "127.0.0.1")
PORT = getattr(settings, "SOCKETIO_PORT", 9000)
MESSAGE_LOG_FORMAT = getattr(settings, "SOCKETIO_MESSAGE_LOG_FORMAT",
                             '%(REMOTE_ADDR)s - - [%(TIME)s] '
                             '"Socket.IO %(TYPE)s: %(MESSAGE)s"')

INSTALLED_APPS = [
    "django_socketio",
]
