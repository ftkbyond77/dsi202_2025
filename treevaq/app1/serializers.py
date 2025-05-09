from rest_framework import serializers
from .models import UserProfile, Order, Product, CarbonFootprint, CommunityPost
from django.contrib.auth.models import User

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['profile_photo']

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=False)  # Allow null profile

    class Meta:
        model = User
        fields = ['username', 'email', 'date_joined', 'profile']

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'order_date', 'total', 'status']

class CarbonFootprintSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarbonFootprint
        fields = ['carbon_saved_kg', 'calculation_notes']

class ProductSerializer(serializers.ModelSerializer):
    carbon_footprint = CarbonFootprintSerializer(read_only=True)
    seller = serializers.StringRelatedField()  # Display the seller's username

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'seller', 'created_at', 'is_sustainable', 'image', 'carbon_footprint']
        read_only_fields = ['id', 'created_at', 'seller']  # Prevent these fields from being updated

    def create(self, validated_data):
        # Automatically set the seller to the authenticated user
        validated_data['seller'] = self.context['request'].user
        return super().create(validated_data)
    
class CommunityPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityPost
        fields = ['id', 'user', 'title', 'content', 'category', 'timestamp', 'likes', 'comments', 'image']