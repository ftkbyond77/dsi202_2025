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
        ('PAID', 'Paid'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ], default='PENDING')

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    receipt = models.ImageField(upload_to='payment_receipts/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('VERIFIED', 'Verified'),
        ('PAID', 'Paid'),
        ('REJECTED', 'Rejected'),
        ('FAILED', 'Failed'),
    ], default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment for Order {self.order.id}"

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

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} for Order {self.order.id}"

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

class CommunityCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    @classmethod
    def get_default_category(cls):
        try:
            return cls.objects.get(id=1)
        except cls.DoesNotExist:
            category, created = cls.objects.get_or_create(
                name='ทั่วไป',
                defaults={
                    'slug': 'general',
                    'description': 'หมวดหมู่ทั่วไปสำหรับโพสต์ทั้งหมด'
                }
            )
            return category

class CommunityPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_posts')
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.ForeignKey(CommunityCategory, on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, blank=True)
    likes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    image = models.ImageField(upload_to='community_images/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while CommunityPost.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
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

class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=RATING_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username}'s review of {self.product.name} ({self.rating}/5)"

    def delete(self, *args, **kwargs):
        self.is_active = False
        self.save()

class Question(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
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