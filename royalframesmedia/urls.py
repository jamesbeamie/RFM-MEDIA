"""authors URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1.4/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import include, path
from django.contrib import admin
from rest_framework_swagger.views import get_swagger_view
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="royalframesmedia",
        default_version='v1',
        description="royalframesmedia media",
        license=openapi.License(name="MIT Licence"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# urls
urlpatterns = [

    path('admin/', admin.site.urls),
    path('photography/royalframesmedia/',
         include('royalframesmedia.apps.authentication.urls')),
    path('photography/royalframesmedia/', include('royalframesmedia.apps.blog.urls')),
    path('photography/royalframesmedia/', include('royalframesmedia.apps.bumps.urls')),
    path('photography/royalframesmedia/', include('royalframesmedia.apps.engagements.urls')),
    path('photography/royalframesmedia/', include('royalframesmedia.apps.family.urls')),
    path('photography/royalframesmedia/', include('royalframesmedia.apps.children.urls')),
    path('photography/royalframesmedia/', include('royalframesmedia.apps.potraits.urls')),
    path('photography/royalframesmedia/', include('royalframesmedia.apps.maevent.urls')),
]
