from django.db import models


class Item(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='items/', )

    def __str__(self):
        return self.name
