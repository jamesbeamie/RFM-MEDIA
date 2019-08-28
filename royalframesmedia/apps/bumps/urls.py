from django.urls import path

from .views import (BumpAPIView, SpecificBump)

app_name = "bumps"

urlpatterns = [
    path('bump/', BumpAPIView.as_view(), name="bump"),
    path('bump/<str:slug>/', SpecificBump.as_view(),
         name="specific/bump"),
]
