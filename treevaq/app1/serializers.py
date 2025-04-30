from rest_framework import serializers
from .models import Product, CarbonFootprint

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