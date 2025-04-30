
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="products")
    created_at = models.DateTimeField(auto_now_add=True)
    is_sustainable = models.BooleanField(default=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    def __str__(self):
        return self.name

class CarbonFootprint(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="carbon_footprint")
    carbon_saved_kg = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0)],
        help_text="Carbon saved in kilograms compared to non-sustainable alternative"
    )
    calculation_notes = models.TextField(blank=True, help_text="Notes on how carbon saving was estimated")

    def calculate_carbon_saving(self):
        if self.product.is_sustainable:
            self.carbon_saved_kg = 1.0
        else:
            self.carbon_saved_kg = 0.0
        self.save()

    def __str__(self):
        return f"Carbon Footprint for {self.product.name}"