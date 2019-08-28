from django.urls import path

from .views import (EngagementAPIView, SpecificEngagement)

app_name = "engagements"

urlpatterns = [
    path('engagements/', EngagementAPIView.as_view(), name="engagements"),
    path('engagements/<str:slug>/', SpecificEngagement.as_view(),
         name="specific/engagement"),
]
