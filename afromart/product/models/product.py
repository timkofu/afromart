from uuid import uuid7

from django.db import models


class Product(models.Model):
    id = models.UUIDField(default=uuid7, primary_key=True, editable=False)
    title = models.CharField(verbose_name="Title")
    description = models.TextField(verbose_name="Description")
    in_stock = models.PositiveIntegerField(verbose_name="In Stock")
    price = models.PositiveBigIntegerField(verbose_name="Price")
    image = models.URLField(verbose_name="Image")  # to-do: cloudinary field
    metadata = models.JSONField(verbose_name="Metadata", blank=True, null=True)

    def __str__(self) -> str:
        return self.title
