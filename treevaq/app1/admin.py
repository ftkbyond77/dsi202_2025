from django.contrib import admin
from django.utils.html import format_html
from .models import (
    UserProfile, Order, OrderItem, Payment, Product, CarbonFootprint, Blog,
    CommunityCategory, CommunityPost, Comment, PostLike, Review, Question, Answer
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'profile_photo']

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
    actions = ['recalculate_carbon_saving']

    def recalculate_carbon_saving(self, request, queryset):
        for footprint in queryset:
            footprint.calculate_carbon_saving()
        self.message_user(request, "Carbon savings recalculated successfully.")
    recalculate_carbon_saving.short_description = "Recalculate carbon savings for selected items"

@admin.register(CommunityCategory)
class CommunityCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(CommunityPost)
class CommunityPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'created_at', 'updated_at')
    search_fields = ('title', 'content', 'user__username')
    list_filter = ('category', 'created_at')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    search_fields = ('user__username', 'post__title')

@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    search_fields = ('user__username', 'post__title')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'created_at')
    search_fields = ('user__username', 'product__name')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'title', 'created_at')
    search_fields = ('user__username', 'product__name', 'title')

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'created_at')
    search_fields = ('user__username', 'question__title')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    search_fields = ('order__id', 'product__name')
    list_filter = ('order__status',)
    readonly_fields = ('price',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'amount', 'status', 'receipt_preview', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order__id', 'order__user__username')
    actions = ['verify_payment', 'reject_payment']

    def receipt_preview(self, obj):
        if obj.receipt:
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.receipt.url)
        return "No receipt"
    receipt_preview.short_description = "Receipt"

    def verify_payment(self, request, queryset):
        queryset.update(status='VERIFIED')
        for payment in queryset:
            payment.order.status = 'SHIPPED'
            payment.order.save()
        self.message_user(request, "Selected payments verified and orders updated to SHIPPED.")
    verify_payment.short_description = "Verify selected payments"

    def reject_payment(self, request, queryset):
        queryset.update(status='REJECTED')
        for payment in queryset:
            payment.order.status = 'CANCELLED'
            payment.order.save()
        self.message_user(request, "Selected payments rejected and orders cancelled.")
    reject_payment.short_description = "Reject selected payments"

# Define OrderItemInline before OrderAdmin
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'order_date', 'total', 'status']
    list_filter = ['status', 'order_date']
    search_fields = ['user__username']
    inlines = [OrderItemInline]  # Reference the inline class