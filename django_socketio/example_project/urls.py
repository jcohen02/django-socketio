
from django.conf.urls import url
from django.urls import include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url('', include('django_socketio.urls')),
    url('', include('chat.urls')),
]
