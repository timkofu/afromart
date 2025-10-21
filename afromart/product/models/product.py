from uuid import uuid7

from django.db import models


class Product(models.Model):
    id = models.UUIDField(default=uuid7, primary_key=True, editable=False)
