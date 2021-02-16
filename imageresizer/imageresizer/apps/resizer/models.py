from django.db import models


# Create your models here.

class Image(models.Model):
    image_name = models.CharField("image_name", max_length=300)
    image_path = models.CharField("image_path", max_length=300)
    add_time = models.DateTimeField("add time")
    def __str__(self):
        return self.image_name