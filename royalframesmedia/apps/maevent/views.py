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

from .models import Events, User
from .renderers import EventsJSONRenderer
from .serializers import EventsSerializer


class EventsAPIView(generics.ListCreateAPIView):
    """
        events endpoints
    """
    queryset = Events.objects.all()
    serializer_class = EventsSerializer

    def post(self, request):
        """
            POST /photography/royalframesmedia/events/
        """
        permission_classes = (IsAuthenticated,)
        context = {"request": request}
        events = request.data.copy()
        events['slug'] = EventsSerializer(
        ).create_slug(request.data['title'])
        serializer = self.serializer_class(data=events, context=context)
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
            GET /photography/royalframesmedia/events/
        """
        perform_pagination = PaginateContent()
        objs_per_page = perform_pagination.paginate_queryset(
            self.queryset, request)
        serializer = EventsSerializer(
            objs_per_page,
            context={
                'request': request
            },
            many=True
        )
        return perform_pagination.get_paginated_response(serializer.data)


class SpecificEvent(generics.RetrieveUpdateDestroyAPIView):
    """
        Specific events endpoint class
    """
    serializer_class = EventsSerializer

    def get(self, request, slug, *args, **kwargs):
        """
            GET /photography/royalframesmedia/events/<slug>/
        """
        try:
            events = Events.objects.get(slug=slug)
        except Events.DoesNotExist:
            raise exceptions.NotFound({
                "message": 'events not found'
            })
        # this checks if an istance of read exists
        # if it doesn't then it creates a new one
        serializer = EventsSerializer(
            events,
            context={
                'request': request
            }
        )
        return Response(serializer.data, status=200)

    def delete(self, request, slug, *args, **kwargs):
        """
            DELETE /photography/royalframesmedia/events/<slug>/
        """
        permission_classes = (IsAuthenticated,)
        try:
            events = Events.objects.get(slug=slug)
        except Events.DoesNotExist:
            raise exceptions.NotFound({
                "message": 'events not found'
            })
        events.delete()
        return Response({
            "events": 'deleted'
        }, status=204)

    def put(self, request, slug, *args, **kwargs):
        """
            PUT /photography/royalframesmedia/events/<slug>/
        """
        permission_classes = (IsAuthenticated,)
        events = get_object_or_404(Events.objects.all(), slug=slug)
        events_data = request.data
        events.updated_at = dt.datetime.utcnow()
        serializer = EventsSerializer(
            instance=events,
            data=events_data,
            context={'request': request},
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                [
                    serializer.data,
                    {"message": 'events updated'}
                ], status=201
            )
        else:
            return Response(
                serializer.errors,
                status=400
            )


def get_events(slug):
    """
        Returns specific events using slug
    """
    events = Events.objects.all().filter(slug=slug).first()
    if events is None:
        raise exceptions.NotFound({
            "message": 'events not found'
        }, status.HTTP_404_NOT_FOUND)
    return events
