from django.db import models
from django.contrib.auth.models import User

class RawMaterial(models.Model):
    name = models.CharField(max_length=255)
    quantity = models.FloatField()
    quality = models.FloatField()

    def __str__(self):
        return self.name

class Processing(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    ]
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE)
    aluminum_output_estimate = models.FloatField(default=0)  # Default value for better handling
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    def calculate_byproducts(self):
        by_products = []
        if self.raw_material.name == "Bauxite Ore":
            by_products = [
                {"name": "Iron Residue", "quantity": 50.0},
                {"name": "Silica Residue", "quantity": 20.0}
            ]
        elif self.raw_material.name == "Aluminum Ore":
            by_products = [
                {"name": "Aluminum Slag", "quantity": 10.0}
            ]
        # Add more conditions if needed for other raw materials
        return by_products

    # def determine_status(self):
    #     # Example thresholds
    #     if self.raw_material.quantity < 10 or self.raw_material.quality < 50:
    #         self.status = 'Failed'
    #     elif self.raw_material.quantity >= 10 and self.raw_material.quality >= 50:
    #         self.status = 'Completed'
    #     else:
    #         self.status = 'Pending'
    #     self.save()

    def __str__(self):
        return f"Processing {self.raw_material.name} - {self.status}"

class ByProduct(models.Model):
    name = models.CharField(max_length=255, default='Unknown')
    quantity = models.FloatField()
    quality = models.CharField(max_length=10, default='Medium')  # Add this line for default value
    processing = models.ForeignKey(Processing, related_name='by_products', on_delete=models.CASCADE)

    def __str__(self):
        return f"ByProduct: {self.name}"

ROLE_CHOICES = [
    ('Admin', 'Admin'),
    ('Operator', 'Operator'),
    ('Viewer', 'Viewer'),
]

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

