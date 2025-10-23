from uuid import uuid7

from django.contrib.postgres.fields import ArrayField
from django.db import models


class Product(models.Model):
    id = models.UUIDField(default=uuid7, primary_key=True, editable=False)
    title = models.CharField(verbose_name="Title")
    description = models.TextField(verbose_name="Description")
    in_stock = models.PositiveIntegerField(verbose_name="In Stock")
    price = models.PositiveBigIntegerField(verbose_name="Price")
    image = models.URLField(verbose_name="Image", blank=True, null=True)
    video = models.URLField(verbose_name="Video", blank=True, null=True)
    tags = ArrayField(
        base_field=models.CharField(), blank=True, null=True, verbose_name="Tags"
    )
    metadata = models.JSONField(verbose_name="Metadata", blank=True, null=True)

    def __str__(self) -> str:
        return self.title
