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

from .models import Potraits, User
from .renderers import PotraitsJSONRenderer
from .serializers import PotraitsSerializer


class PotraitsAPIView(generics.ListCreateAPIView):
    """
        family endpoints
    """
    queryset = Potraits.objects.all()
    serializer_class = PotraitsSerializer

    def post(self, request):
        """
            POST /photography/royalframesmedia/Potraits/
        """
        permission_classes = (IsAuthenticated,)
        context = {"request": request}
        potraits = request.data.copy()
        potraits['slug'] = PotraitsSerializer(
        ).create_slug(request.data['title'])
        serializer = self.serializer_class(data=potraits, context=context)
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
            GET /photography/royalframesmedia/potraits/
        """
        perform_pagination = PaginateContent()
        objs_per_page = perform_pagination.paginate_queryset(
            self.queryset, request)
        serializer = PotraitsSerializer(
            objs_per_page,
            context={
                'request': request
            },
            many=True
        )
        return perform_pagination.get_paginated_response(serializer.data)


class SpecificPotrait(generics.RetrieveUpdateDestroyAPIView):
    """
        Specific potraits endpoint class
    """
    serializer_class = PotraitsSerializer

    def get(self, request, slug, *args, **kwargs):
        """
            GET /photography/royalframesmedia/potraits/<slug>/
        """
        try:
            potraits = Potraits.objects.get(slug=slug)
        except Potraits.DoesNotExist:
            raise exceptions.NotFound({
                "message": 'potrait not found'
            })
        # this checks if an istance of read exists
        # if it doesn't then it creates a new one
        serializer = PotraitsSerializer(
            potraits,
            context={
                'request': request
            }
        )
        return Response(serializer.data, status=200)

    def delete(self, request, slug, *args, **kwargs):
        """
            DELETE /photography/royalframesmedia/potraits/<slug>/
        """
        permission_classes = (IsAuthenticated,)
        try:
            potraits = Potraits.objects.get(slug=slug)
        except Potraits.DoesNotExist:
            raise exceptions.NotFound({
                "message": 'potrait not found'
            })
        potraits.delete()
        return Response({
            "potraits": 'deleted'
        }, status=204)

    def put(self, request, slug, *args, **kwargs):
        """
            PUT /photography/royalframesmedia/potraits/<slug>/
        """
        permission_classes = (IsAuthenticated,)
        potraits = get_object_or_404(Potraits.objects.all(), slug=slug)
        potraits_data = request.data
        potraits.updated_at = dt.datetime.utcnow()
        serializer = PotraitsSerializer(
            instance=potraits,
            data=potraits_data,
            context={'request': request},
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                [
                    serializer.data,
                    {"message": 'potraits updated'}
                ], status=201
            )
        else:
            return Response(
                serializer.errors,
                status=400
            )


def get_potraits(slug):
    """
        Returns specific potraits using slug
    """
    potraits = Potraits.objects.all().filter(slug=slug).first()
    if potraits is None:
        raise exceptions.NotFound({
            "message": 'potrait not found'
        }, status.HTTP_404_NOT_FOUND)
    return potraits
