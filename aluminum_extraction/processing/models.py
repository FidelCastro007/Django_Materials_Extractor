from django.db import models
from django.contrib.auth.models import User

class RawMaterial(models.Model):
    name = models.CharField(max_length=255)
    quantity = models.FloatField()
    quality = models.FloatField()

    def __str__(self):
        return self.name

class Processing(models.Model):
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE)
    aluminum_output_estimate = models.FloatField(default=0)  # Add a default value here
    status = models.CharField(max_length=20)

class ByProduct(models.Model):
    name = models.CharField(max_length=255, default='Unknown')
    quantity = models.FloatField()
    processing = models.ForeignKey(Processing, related_name='by_products', on_delete=models.CASCADE)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20)
