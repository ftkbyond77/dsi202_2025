from django.contrib import admin
from .models import UserProfile, Order, Product, CarbonFootprint, Blog, CommunityPost

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'profile_photo']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'order_date', 'total', 'status']
    list_filter = ['status', 'order_date']
    search_fields = ['user__username']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'seller', 'is_sustainable', 'created_at')
    list_filter = ('is_sustainable', 'created_at')
    search_fields = ('name', 'description', 'seller__username')
    ordering = ('-created_at',)

@admin.register(CarbonFootprint)
class CarbonFootprintAdmin(admin.ModelAdmin):
    list_display = ('product', 'carbon_saved_kg')
    search_fields = ('product__name',)
    readonly_fields = ('carbon_saved_kg',)

    # Optional: Custom admin action to recalculate carbon savings
    actions = ['recalculate_carbon_saving']

    def recalculate_carbon_saving(self, request, queryset):
        for footprint in queryset:
            footprint.calculate_carbon_saving()
        self.message_user(request, "Carbon savings recalculated successfully.")
    recalculate_carbon_saving.short_description = "Recalculate carbon savings for selected items"

admin.site.register(Blog)
admin.site.register(CommunityPost)