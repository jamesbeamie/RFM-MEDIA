import datetime as dt
import json
import os
import random
import re
from datetime import datetime, timedelta

import django
from django.core.mail import send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string

from royalframesmedia.apps.authentication.utils import status_codes, swagger_body
from royalframesmedia.apps.core.pagination import PaginateContent
from drf_yasg import openapi
from drf_yasg.inspectors import SwaggerAutoSchema
from drf_yasg.utils import swagger_auto_schema, swagger_serializer_method
from rest_framework import exceptions, generics, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.views import Response

from .models import Engagement, User
from .renderers import EngagementJSONRenderer
from .serializers import EngagementSerializer


class EngagementAPIView(generics.ListCreateAPIView):
    """
        engagement endpoints
    """
    queryset = Engagement.objects.all()
    serializer_class = EngagementSerializer

    def post(self, request):
        """
            POST /photography/royalframesmedia/engagements/
        """
        permission_classes = (IsAuthenticated,)
        context = {"request": request}
        engagement = request.data.copy()
        engagement['slug'] = EngagementSerializer(
        ).create_slug(request.data['title'])
        serializer = self.serializer_class(data=engagement, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def get(self, request):
        """
            GET /photography/royalframesmedia/engagements/
        """
        perform_pagination = PaginateContent()
        objs_per_page = perform_pagination.paginate_queryset(
            self.queryset, request)
        serializer = EngagementSerializer(
            objs_per_page,
            context={
                'request': request
            },
            many=True
        )
        return perform_pagination.get_paginated_response(serializer.data)


class SpecificEngagement(generics.RetrieveUpdateDestroyAPIView):
    """
        Specific engagement endpoint class
    """
    serializer_class = EngagementSerializer

    def get(self, request, slug, *args, **kwargs):
        """
            GET /photography/royalframesmedia/engagements/<slug>/
        """
        try:
            engagement = Engagement.objects.get(slug=slug)
        except Engagement.DoesNotExist:
            raise exceptions.NotFound({
                "message": 'engagements not found'
            })
        # this checks if an istance of read exists
        # if it doesn't then it creates a new one
        serializer = EngagementSerializer(
            engagement,
            context={
                'request': request
            }
        )
        return Response(serializer.data, status=200)

    def delete(self, request, slug, *args, **kwargs):
        """
            DELETE /photography/royalframesmedia/engagements/<slug>/
        """
        permission_classes = (IsAuthenticated,)
        try:
            engagement = Engagement.objects.get(slug=slug)
        except Engagement.DoesNotExist:
            raise exceptions.NotFound({
                "message": 'engagements not found'
            })
        engagement.delete()
        return Response({
            "engagement": 'deleted'
        }, status=204)

    def put(self, request, slug, *args, **kwargs):
        """
            PUT /photography/royalframesmedia/engagements/<slug>/
        """
        permission_classes = (IsAuthenticated,)
        engagement = get_object_or_404(Engagement.objects.all(), slug=slug)
        engagement_data = request.data
        engagement.updated_at = dt.datetime.utcnow()
        serializer = EngagementSerializer(
            instance=engagement,
            data=engagement_data,
            context={'request': request},
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                [
                    serializer.data,
                    {"message": 'engagement updated'}
                ], status=201
            )
        else:
            return Response(
                serializer.errors,
                status=400
            )


def get_Engagement(slug):
    """
        Returns specific engagement using slug
    """
    engagement = Engagement.objects.all().filter(slug=slug).first()
    if engagement is None:
        raise exceptions.NotFound({
            "message": 'not found'
        }, status.HTTP_404_NOT_FOUND)
    return engagement
