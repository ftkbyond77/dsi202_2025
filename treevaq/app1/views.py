from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
from django.views.generic import ListView, DetailView
from .models import Product, CarbonFootprint, Blog, CommunityPost, User
from django.db.models import Q, Sum, Avg, Count
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test, login_required
from rest_framework import generics, permissions
from .serializers import ProductSerializer

from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib import messages
from .forms import ProductPostForm, ReviewForm, QuestionForm, AnswerForm

import json
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.views import generic

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .serializers import UserSerializer, OrderSerializer
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist

class SignupView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'app1/signup.html'

def home(request):
    return render(request, 'app1/home.html')

def product_list(request):
    return render(request, 'app1/product_list.html')

def blog(request):
    return render(request, 'app1/blog.html')

def community(request):
    return render(request, 'app1/community.html')

def dashboard(request):
    return render(request, 'app1/dashboard.html')

def view_cart(request):
    return render(request, 'app1/cart.html')

def product_detail(request, pk):
    return render(request, 'app1/product_detail.html')

def blog_detail(request, pk):
    return render(request, 'app1/blog_detail.html')

# Template Views
def home(request):
    return render(request, 'app1/home.html')


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            serializer = UserSerializer(request.user)
            return Response(serializer.data)
        except ObjectDoesNotExist as e:
            return Response({'error': 'User profile not found. Please contact support.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        user_profile = request.user.profile
        if 'profile_photo' in request.FILES:
            user_profile.profile_photo = request.FILES['profile_photo']
            user_profile.save()
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        form = PasswordChangeForm(user=request.user, data=request.data)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return Response({'message': 'Password updated successfully'}, status=status.HTTP_200_OK)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            orders = request.user.orders.all().order_by('-order_date')
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': f'Failed to fetch orders: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@login_required
def account_view(request):
    return render(request, 'app1/account.html')

class ProductListView(ListView):
    model = Product
    template_name = 'app1/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        sustainable_filter = self.request.GET.get('sustainable', False)
        queryset = super().get_queryset()
        if query:
            queryset = queryset.filter(Q(name__icontains=query) | Q(description__icontains=query))
        if sustainable_filter:
            queryset = queryset.filter(is_sustainable=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['sustainable_filter'] = self.request.GET.get('sustainable', False)
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'app1/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Use the OneToOneField related name: carbon_footprint
        carbon_footprint = getattr(self.object, 'carbon_footprint', None)
        if carbon_footprint:
            total_carbon_saved = carbon_footprint.carbon_saved_kg
            context['total_carbon_saved'] = total_carbon_saved
            context['has_carbon_footprints'] = True
        else:
            context['total_carbon_saved'] = 0.0
            context['has_carbon_footprints'] = False
        return context

@login_required
def dashboard(request):
    # Existing Metrics
    total_products = Product.objects.count()
    sustainable_products = Product.objects.filter(is_sustainable=True).count()
    total_carbon_saved = CarbonFootprint.objects.aggregate(total=Sum('carbon_saved_kg'))['total'] or 0.0
    average_price = Product.objects.aggregate(avg_price=Avg('price'))['avg_price'] or 0.0
    average_price = round(average_price, 2)
    products_per_seller = User.objects.annotate(
        product_count=Count('products')
    ).values('username', 'product_count').filter(product_count__gt=0)

    # User Statistics
    total_users = User.objects.count()
    thirty_days_ago = datetime.now() - timedelta(days=30)
    active_users = User.objects.filter(last_login__gte=thirty_days_ago).count()
    active_percentage = round((active_users / total_users * 100) if total_users > 0 else 0, 1)
    recent_users = User.objects.order_by('-last_login')[:5]

    # Carbon Savings Equivalents (Simplified Calculations)
    carbon_equivalent_trees = round(total_carbon_saved / 20)  # Approx. 20 kg CO₂ per tree per year
    carbon_equivalent_cars = round(total_carbon_saved / 4700)  # Approx. 4700 kg CO₂ per car per year

    # Average Metrics
    products_per_user = round(Product.objects.count() / total_users, 1) if total_users > 0 else 0

    # Simulated Order Data (Replace with actual Order model in a real implementation)
    total_orders = 120  # Simulated
    total_revenue = 4500.00  # Simulated
    recent_orders = [
        {'id': 1, 'user': User.objects.first() or {'username': 'user1'}, 'total_amount': 150.00, 'created_at': datetime.now(), 'status': 'completed'},
        {'id': 2, 'user': User.objects.first() or {'username': 'user2'}, 'total_amount': 200.00, 'created_at': datetime.now() - timedelta(days=1), 'status': 'pending'},
        {'id': 3, 'user': User.objects.first() or {'username': 'user3'}, 'total_amount': 80.00, 'created_at': datetime.now() - timedelta(days=2), 'status': 'completed'},
    ]

    # Simulated Top Products (Replace with actual data in a real implementation)
    top_products = [
        {'name': 'Eco-Friendly Bag', 'units_sold': 50, 'revenue': 1000.00, 'is_sustainable': True},
        {'name': 'Reusable Water Bottle', 'units_sold': 40, 'revenue': 800.00, 'is_sustainable': True},
        {'name': 'Plastic Container', 'units_sold': 30, 'revenue': 450.00, 'is_sustainable': False},
        {'name': 'Bamboo Toothbrush', 'units_sold': 25, 'revenue': 125.00, 'is_sustainable': True},
        {'name': 'Cotton Tote', 'units_sold': 20, 'revenue': 300.00, 'is_sustainable': True},
    ]

    context = {
        'total_products': total_products,
        'sustainable_products': sustainable_products,
        'total_carbon_saved': total_carbon_saved,
        'average_price': average_price,
        'products_per_seller': products_per_seller,
        'total_users': total_users,
        'active_users': active_users,
        'active_percentage': active_percentage,
        'recent_users': recent_users,
        'carbon_equivalent_trees': carbon_equivalent_trees,
        'carbon_equivalent_cars': carbon_equivalent_cars,
        'products_per_user': products_per_user,
        'average_rating': None,  # Placeholder (requires a Product rating field)
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
        'top_products': top_products,
    }
    return render(request, 'app1/dashboard.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser)  # Only allow superusers
def user_management(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'app1/user_management.html', {'users': users})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def edit_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        # Handle form submission
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.save()
        messages.success(request, f"User {user.username} updated successfully")
        return redirect('app1:user_management')
    return render(request, 'app1/edit_user.html', {'user': user})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def activate_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.is_active = True
    user.save()
    messages.success(request, f"User {user.username} activated")
    return redirect('app1:user_management')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def deactivate_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.is_active = False
    user.save()
    messages.warning(request, f"User {user.username} deactivated")
    return redirect('app1:user_management')

@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart = request.session.get('cart', {})
    cart[product.pk] = cart.get(product.pk, 0) + 1
    request.session['cart'] = cart
    return redirect('app1:product_detail', pk=pk)

@login_required
def view_cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, pk=product_id)
        subtotal = product.price * quantity
        total += subtotal
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })
    context = {
        'cart_items': cart_items,
        'total': total
    }
    return render(request, 'app1/cart.html', context)

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('app1:view_cart')
    cart_items = []
    total = 0
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, pk=product_id)
        subtotal = product.price * quantity
        total += subtotal
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })
    if request.method == 'POST':
        # Simulate order placement (no payment system)
        del request.session['cart']  # Clear cart after checkout
        return redirect('app1:home')
    context = {
        'cart_items': cart_items,
        'total': total
    }
    return render(request, 'app1/checkout.html', context)

@login_required
def blog(request):
    articles = Blog.objects.all()
    context = {
        'articles': articles
    }
    return render(request, 'app1/blog.html', context)

@login_required
def blog_detail(request, article_id):
    article = get_object_or_404(Blog, id=article_id)
    context = {'article': article}
    return render(request, 'app1/blog_details.html', context)

@login_required
def community(request):
    # Initialize Review Form
    review_form = ReviewForm(request.POST if request.method == 'POST' else None)

    # Handle Form Submissions (for reviews)
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'review' and review_form.is_valid():
            review_form.save(request.user)
            messages.success(request, "Review submitted successfully!")
            return redirect('app1:community')
        
        # Handle Voting
        elif request.POST.get('action') == 'vote':
            post_id = request.POST.get('post_id')
            vote_type = request.POST.get('vote_type')
            post = get_object_or_404(CommunityPost, id=post_id)
            if vote_type == 'upvote':
                post.upvotes += 1
            elif vote_type == 'downvote':
                post.downvotes += 1
            post.save()
            return redirect('app1:community')

    # Fetch Products and Associated Reviews
    products = Product.objects.all()
    # Simulate topics (since Product model doesn't have this field)
    for product in products:
        product.topics = ["Sustainable"] if product.is_sustainable else ["General"]
        if "Bag" in product.name:
            product.topics.append("Fashion")
        elif "Bottle" in product.name or "Container" in product.name:
            product.topics.append("Kitchen")
        elif "Toothbrush" in product.name:
            product.topics.append("Personal Care")
        else:
            product.topics.append("Miscellaneous")

    # Fetch reviews for each product
    product_reviews = {
        product.id: CommunityPost.objects.filter(product=product, post_type='REVIEW')
        for product in products
    }

    # Calculate Carbon Savers Ranking with Levels
    carbon_ranking = CarbonFootprint.objects.values('product__seller__username').annotate(total_carbon_saved=Sum('carbon_saved_kg')).order_by('-total_carbon_saved')[:5]
    ranking_list = []
    for item in carbon_ranking:
        if not item['product__seller__username']:
            continue
        carbon_saved = item['total_carbon_saved'] or 0.0
        # Determine level based on carbon saved
        if carbon_saved >= 50:
            level = "Expert"
        elif carbon_saved >= 20:
            level = "Advanced"
        elif carbon_saved >= 5:
            level = "Student"
        else:
            level = "Basic"
        # Simulate a description for the user (since User model doesn't have a description field)
        description = f"Eco-warrior contributing to a greener planet with {carbon_saved:.2f} kg saved!"
        ranking_list.append({
            'username': item['product__seller__username'],
            'carbon_saved': carbon_saved,
            'description': description,
            'level': level,
        })

    context = {
        'review_form': review_form,
        'products': products,
        'product_reviews': product_reviews,
        'carbon_ranking': ranking_list,
    }
    return render(request, 'app1/community.html', context)

@login_required
def add_to_wishlist(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        if not product_id:
            return JsonResponse({'status': 'error', 'message': 'Product ID is required'}, status=400)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Product not found'}, status=404)

        # Get or initialize wishlist from session
        wishlist = request.session.get('wishlist', [])
        if product_id not in wishlist:
            wishlist.append(product_id)
            request.session['wishlist'] = wishlist
            return JsonResponse({'status': 'success', 'message': f'Added {product.name} to wishlist!'})
        else:
            return JsonResponse({'status': 'info', 'message': f'{product.name} is already in your wishlist!'})
    elif request.method == 'GET':
        # Return the current wishlist count for the client
        wishlist = request.session.get('wishlist', [])
        return JsonResponse({'wishlist_count': len(wishlist)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required
def remove_from_wishlist(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        if not product_id:
            return JsonResponse({'status': 'error', 'message': 'Product ID is required'}, status=400)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Product not found'}, status=404)

        # Get or initialize wishlist from session
        wishlist = request.session.get('wishlist', [])
        if product_id in wishlist:
            wishlist.remove(product_id)
            request.session['wishlist'] = wishlist
            return JsonResponse({'status': 'success', 'message': f'Removed {product.name} from wishlist!'})
        else:
            return JsonResponse({'status': 'info', 'message': f'{product.name} is not in your wishlist!'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required
def wishlist(request):
    # Get wishlist from session
    wishlist = request.session.get('wishlist', [])
    # Fetch product objects for the wishlist
    products = Product.objects.filter(id__in=wishlist)
    context = {
        'wishlist': products,
    }
    return render(request, 'app1/wishlist.html', context)

# API Views
class ProductListCreateAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ProductRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        if self.request.user != serializer.instance.seller:
            raise permissions.PermissionDenied("You can only update your own products.")
        serializer.save()