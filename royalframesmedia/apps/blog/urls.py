from django.urls import path

from .views import (BlogAPIView, SpecificBlog)

app_name = "blog"

urlpatterns = [
    path('blog/', BlogAPIView.as_view(), name="blog"),
    path('blog/<str:slug>/', SpecificBlog.as_view(),
         name="specific/blog"),
]
