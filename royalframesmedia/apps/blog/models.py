from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.template.defaultfilters import slugify

from royalframesmedia.apps.authentication.models import User
from cloudinary.models import CloudinaryField


class Blog(models.Model):
    """
        Each Blog model schema
    """
    image_path = models.CharField(max_length=255, blank=True, null=True)
    slug = models.SlugField(max_length=255)
    title = models.CharField(db_index=True, max_length=255)
    tag = models.CharField(db_index=True, max_length=255)
    description = models.CharField(db_index=True, max_length=255)
    body = models.CharField(db_index=True, max_length=8055)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    def __str__(self):
        return self.body
