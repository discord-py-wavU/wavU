from django.urls import path

from .views import *

urlpatterns = [
    path("count_server/", CountServer.as_view()),
]
