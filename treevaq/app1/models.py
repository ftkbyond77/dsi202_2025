
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
    
class Blog(models.Model):
    title = models.CharField(max_length=200)
    summary = models.TextField()
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='blog_posts')
    image = models.ImageField(upload_to='blog_images/', null=True, blank=True)
    published_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
class CommunityPost(models.Model):
    POST_TYPES = (
        ('PRODUCT_POST', 'Product Post'),
        ('REVIEW', 'Review/Rating'),
        ('QUESTION', 'Question'),
        ('ANSWER', 'Answer'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_posts')
    post_type = models.CharField(max_length=20, choices=POST_TYPES)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='community_posts', null=True, blank=True)
    content = models.TextField()
    rating = models.IntegerField(null=True, blank=True, help_text="Rating out of 5 (for reviews only)")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', help_text="For answers to questions")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.post_type} - {self.created_at}"