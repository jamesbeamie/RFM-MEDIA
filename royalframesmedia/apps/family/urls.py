from django.urls import path

from .views import (BumpAPIView, SpecificBump)

app_name = "family"

urlpatterns = [
    path('family/', BumpAPIView.as_view(), name="family"),
    path('family/<str:slug>/', SpecificBump.as_view(),
         name="specific/family"),
]
