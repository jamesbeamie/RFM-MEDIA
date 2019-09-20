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

from .models import Bump, User
from .renderers import BumpJSONRenderer
from .serializers import BumpSerializer


class BumpAPIView(generics.ListCreateAPIView):
    """
        bump endpoints
    """
    queryset = Bump.objects.all()
    serializer_class = BumpSerializer

    def post(self, request):
        """
            POST /photography/royalframesmedia/bump/
        """
        permission_classes = (IsAuthenticatedOrReadOnly,)
        if permission_classes:
            context = {"request": request}
            bump = request.data.copy()
            bump['slug'] = BumpSerializer(
            ).create_slug(request.data['title'])
            serializer = self.serializer_class(data=bump, context=context)
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
        return Response(
            serializer.errors,
            status=status.HTTP_401_UNAUTHORIZED
        )

    def get(self, request):
        """
            GET /photography/royalframesmedia/bump/
        """
        perform_pagination = PaginateContent()
        objs_per_page = perform_pagination.paginate_queryset(
            self.queryset, request)
        serializer = BumpSerializer(
            objs_per_page,
            context={
                'request': request
            },
            many=True
        )
        return perform_pagination.get_paginated_response(serializer.data)


class SpecificBump(generics.RetrieveUpdateDestroyAPIView):
    """
        Specific bump endpoint class
    """
    serializer_class = BumpSerializer

    def get(self, request, slug, *args, **kwargs):
        """
            GET /photography/royalframesmedia/bump/<slug>/
        """
        try:
            bump = Bump.objects.get(slug=slug)
        except Bump.DoesNotExist:
            raise exceptions.NotFound({
                "message": 'Bump not found'
            })
        # this checks if an istance of read exists
        # if it doesn't then it creates a new one
        serializer = BumpSerializer(
            bump,
            context={
                'request': request
            }
        )
        return Response(serializer.data, status=200)

    def delete(self, request, slug, *args, **kwargs):
        """
            DELETE /photography/royalframesmedia/bump/<slug>/
        """
        permission_classes = (IsAuthenticated,)
        try:
            bump = Bump.objects.get(slug=slug)
        except Bump.DoesNotExist:
            raise exceptions.NotFound({
                "message": 'Bump not found'
            })
        bump.delete()
        return Response({
            "bump": 'deleted'
        }, status=204)

    def put(self, request, slug, *args, **kwargs):
        """
            PUT /photography/royalframesmedia/bump/<slug>/
        """
        permission_classes = (IsAuthenticated,)
        bump = get_object_or_404(Bump.objects.all(), slug=slug)
        bump_data = request.data
        bump.updated_at = dt.datetime.utcnow()
        serializer = BumpSerializer(
            instance=bump,
            data=bump_data,
            context={'request': request},
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                [
                    serializer.data,
                    {"message": 'bump updated'}
                ], status=201
            )
        else:
            return Response(
                serializer.errors,
                status=400
            )


def get_bump(slug):
    """
        Returns specific bump using slug
    """
    bump = Bump.objects.all().filter(slug=slug).first()
    if bump is None:
        raise exceptions.NotFound({
            "message": 'Bump not found'
        }, status.HTTP_404_NOT_FOUND)
    return bump
