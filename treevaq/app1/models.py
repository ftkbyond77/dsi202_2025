
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils.text import slugify
from django.urls import reverse

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_date = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'Pending'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ], default='PENDING')

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

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
    
# class CommunityPost(models.Model):
#     POST_TYPES = (
#         ('PRODUCT_POST', 'Product Post'),
#         ('REVIEW', 'Review/Rating'),
#         ('QUESTION', 'Question'),
#         ('ANSWER', 'Answer'),
#     )

#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_posts')
#     post_type = models.CharField(max_length=20, choices=POST_TYPES)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='community_posts', null=True, blank=True)
#     content = models.TextField()
#     rating = models.IntegerField(null=True, blank=True, help_text="Rating out of 5 (for reviews only)")
#     parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', help_text="For answers to questions")
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     upvotes = models.IntegerField(default=0)
#     downvotes = models.IntegerField(default=0)

#     def __str__(self):
#         return f"{self.user.username} - {self.post_type} - {self.created_at}"

# Community-related models
class CommunityCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Community Categories"


class CommunityPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_posts')
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.ForeignKey(CommunityCategory, on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, blank=True)
    likes_count = models.IntegerField(default=0)  # Add this
    comments_count = models.IntegerField(default=0)  # Add this
    image = models.ImageField(upload_to='community_images/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def likes_count(self):
        return self.likes.count()
    
    @property
    def comments_count(self):
        return self.comments.count()
    
    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'slug': self.slug})


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title}"


class PostLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_likes')
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
    
    def __str__(self):
        return f"{self.user.username} likes {self.post.title}"


# IMPORTANT: DO NOT MODIFY THE PRODUCT MODEL IF IT ALREADY EXISTS
# Instead, define the models that reference it

# Add these if they don't exist yet
class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    # Assuming your Product model is imported or defined elsewhere
    # Use this if the Product model is in another app:
    # product = models.ForeignKey('other_app.Product', on_delete=models.CASCADE, related_name='reviews')
    # Or use this if the Product model is in the same app:
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=RATING_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s review of {self.product.name}"


class Question(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    # Assuming your Product model is imported or defined elsewhere
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='questions')
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    @property
    def answers_count(self):
        return self.answers.count()


class Answer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Answer by {self.user.username} to {self.question.title}"

# NOTE: If this is a new addition to your models.py file,
# you'll need to run makemigrations and migrate.
# If you're uncertain about the structure of your existing Product model,
# consider checking it first or using Django's 'inspectdb' command.