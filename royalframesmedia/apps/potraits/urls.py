from django.urls import path

from .views import (PotraitsAPIView, SpecificPotrait)

app_name = "potraits"

urlpatterns = [
    path('potraits/', PotraitsAPIView.as_view(), name="potraits"),
    path('potraits/<str:slug>/', SpecificPotrait.as_view(),
         name="specific/potraits"),
]
