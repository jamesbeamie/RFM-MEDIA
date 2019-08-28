from django.urls import path

from .views import (ChildrenAPIView, SpecificChild)

app_name = "childrens"

urlpatterns = [
    path('children/', ChildrenAPIView.as_view(), name="children"),
    path('children/<str:slug>/', SpecificChild.as_view(),
         name="specific/children"),
]
