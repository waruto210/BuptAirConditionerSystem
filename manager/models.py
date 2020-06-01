from django.db import models

# Create your models here.
class Forms(models.Model):

    title = models.CharField(max_length=100)
    use_time = models.IntegerField()