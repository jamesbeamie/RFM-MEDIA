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

from .models import Blog, User
from .renderers import BlogJSONRenderer
from .serializers import BlogSerializer


class BlogAPIView(generics.ListCreateAPIView):
    """
        Article endpoints
    """
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer

    def post(self, request):
        """
            POST /photography/royalframesmedia/Blog/
        """
        permission_classes = (IsAuthenticated,)
        context = {"request": request}
        blog = request.data.copy()
        blog['slug'] = BlogSerializer(
        ).create_slug(request.data['tag'])
        serializer = self.serializer_class(data=blog, context=context)
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
            GET /photography/royalframesmedia/blog/
        """
        perform_pagination = PaginateContent()
        objs_per_page = perform_pagination.paginate_queryset(
            self.queryset, request)
        serializer = BlogSerializer(
            objs_per_page,
            context={
                'request': request
            },
            many=True
        )
        return perform_pagination.get_paginated_response(serializer.data)


class SpecificBlog(generics.RetrieveUpdateDestroyAPIView):
    """
        Specific blog endpoint class
    """
    serializer_class = BlogSerializer

    def get(self, request, slug, *args, **kwargs):
        """
            GET /photography/royalframesmedia/blog/<slug>/
        """
        try:
            blog = Blog.objects.get(slug=slug)
        except Blog.DoesNotExist:
            raise exceptions.NotFound({
                "message": 'blog not found'
            })
        # this checks if an istance of read exists
        # if it doesn't then it creates a new one
        serializer = BlogSerializer(
            blog,
            context={
                'request': request
            }
        )
        return Response(serializer.data, status=200)

    def delete(self, request, slug, *args, **kwargs):
        """
            DELETE /photography/royalframesmedia/blog/<slug>/
        """
        permission_classes = (IsAuthenticated,)
        try:
            blog = Blog.objects.get(slug=slug)
        except Blog.DoesNotExist:
            raise exceptions.NotFound({
                "message": 'blog not found'
            })
        blog.delete()
        return Response({
            "blog": 'deleted'
        }, status=204)

    def put(self, request, slug, *args, **kwargs):
        """
            PUT /photography/royalframesmedia/blog/<slug>/
        """
        permission_classes = (IsAuthenticated,)
        blog = get_object_or_404(Blog.objects.all(), slug=slug)
        blog_data = request.data
        blog.updated_at = dt.datetime.utcnow()
        serializer = BlogSerializer(
            instance=blog,
            data=blog_data,
            context={'request': request},
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                [
                    serializer.data,
                    {"message": 'blog updated'}
                ], status=201
            )
        else:
            return Response(
                serializer.errors,
                status=400
            )


def get_blog(slug):
    """
        Returns specific blog using slug
    """
    blog = Blog.objects.all().filter(slug=slug).first()
    if blog is None:
        raise exceptions.NotFound({
            "message": 'blog not found'
        }, status.HTTP_404_NOT_FOUND)
    return blog
