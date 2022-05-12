from django.db import models


class Course(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name