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

from .models import Family, User
from .renderers import FamilyJSONRenderer
from .serializers import FamilySerializer


class BumpAPIView(generics.ListCreateAPIView):
    """
        family endpoints
    """
    queryset = Family.objects.all()
    serializer_class = FamilySerializer

    def post(self, request):
        """
            POST /photography/royalframesmedia/family/
        """
        permission_classes = (IsAuthenticated,)
        context = {"request": request}
        family = request.data.copy()
        family['slug'] = FamilySerializer(
        ).create_slug(request.data['title'])
        serializer = self.serializer_class(data=family, context=context)
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
            GET /photography/royalframesmedia/family/
        """
        perform_pagination = PaginateContent()
        objs_per_page = perform_pagination.paginate_queryset(
            self.queryset, request)
        serializer = FamilySerializer(
            objs_per_page,
            context={
                'request': request
            },
            many=True
        )
        return perform_pagination.get_paginated_response(serializer.data)


class SpecificBump(generics.RetrieveUpdateDestroyAPIView):
    """
        Specific family endpoint class
    """
    serializer_class = FamilySerializer

    def get(self, request, slug, *args, **kwargs):
        """
            GET /photography/royalframesmedia/family/<slug>/
        """
        try:
            family = Family.objects.get(slug=slug)
        except Family.DoesNotExist:
            raise exceptions.NotFound({
                "message": 'family not found'
            })
        # this checks if an istance of read exists
        # if it doesn't then it creates a new one
        serializer = FamilySerializer(
            family,
            context={
                'request': request
            }
        )
        return Response(serializer.data, status=200)

    def delete(self, request, slug, *args, **kwargs):
        """
            DELETE /photography/royalframesmedia/family/<slug>/
        """
        permission_classes = (IsAuthenticated,)
        try:
            family = Family.objects.get(slug=slug)
        except Family.DoesNotExist:
            raise exceptions.NotFound({
                "message": 'family not found'
            })
        family.delete()
        return Response({
            "family": 'deleted'
        }, status=204)

    def put(self, request, slug, *args, **kwargs):
        """
            PUT /photography/royalframesmedia/family/<slug>/
        """
        permission_classes = (IsAuthenticated,)
        family = get_object_or_404(Family.objects.all(), slug=slug)
        family_data = request.data
        family.updated_at = dt.datetime.utcnow()
        serializer = FamilySerializer(
            instance=family,
            data=family_data,
            context={'request': request},
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                [
                    serializer.data,
                    {"message": 'family updated'}
                ], status=201
            )
        else:
            return Response(
                serializer.errors,
                status=400
            )


def get_family(slug):
    """
        Returns specific family using slug
    """
    family = Family.objects.all().filter(slug=slug).first()
    if family is None:
        raise exceptions.NotFound({
            "message": 'family not found'
        }, status.HTTP_404_NOT_FOUND)
    return family
