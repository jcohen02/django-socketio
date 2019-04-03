
from django.conf.urls import url
from .views import rooms, create, system_message, room


urlpatterns = [
    url("^$", rooms, name="rooms"),
    url("^create/$", create, name="create"),
    url("^system_message/$", system_message, name="system_message"),
    url("^(?P<slug>.*)$", room, name="room"),
]
