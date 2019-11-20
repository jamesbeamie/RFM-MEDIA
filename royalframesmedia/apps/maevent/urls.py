from django.urls import path

from .views import (EventsAPIView, SpecificEvent)

app_name = "maevent"

urlpatterns = [
    path('events/', EventsAPIView.as_view(), name="events"),
    path('events/<str:slug>/', SpecificEvent.as_view(),
         name="specific/events"),
]
