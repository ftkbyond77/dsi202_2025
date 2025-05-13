from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
from django.views.generic import ListView, DetailView
from .models import Product, CarbonFootprint, Blog, CommunityPost, User, PostLike, Comment, CommunityCategory, Review, Order, OrderItem, Payment
from django.db.models import Q, Sum, Avg, Count
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test, login_required
from rest_framework import generics, permissions
from .serializers import ProductSerializer, UserSerializer, OrderSerializer, CommunityPostSerializer
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib import messages
from .forms import ProductPostForm, ReviewForm, QuestionForm, AnswerForm
import json
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.views import generic
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import qrcode
import os
from app1.pypromptpay import qr_code
import logging

# Initialize logger
logger = logging.getLogger(__name__)

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
    review_form = ReviewForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        if form_type == 'review' and review_form.is_valid():
            review_form.save(request.user)
            messages.success(request, "Review submitted successfully!")
            return redirect('app1:community')
    posts = CommunityPost.objects.all().order_by('-created_at')
    categories = CommunityCategory.objects.all()
    category_id = request.GET.get('category')
    if category_id:
        posts = posts.filter(category_id=category_id)
    products = Product.objects.all()
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
    carbon_ranking = CarbonFootprint.objects.values('product__seller__username').annotate(
        total_carbon_saved=Sum('carbon_saved_kg')
    ).order_by('-total_carbon_saved')[:5]
    ranking_list = []
    for item in carbon_ranking:
        if not item['product__seller__username']:
            continue
        carbon_saved = item['total_carbon_saved'] or 0.0
        if carbon_saved >= 50:
            level = "Expert"
        elif carbon_saved >= 20:
            level = "Advanced"
        elif carbon_saved >= 5:
            level = "Student"
        else:
            level = "Basic"
        description = f"Eco-warrior contributing to a greener planet with {carbon_saved:.2f} kg saved!"
        ranking_list.append({
            'username': item['product__seller__username'],
            'carbon_saved': carbon_saved,
            'description': description,
            'level': level,
        })
    context = {
        'review_form': review_form,
        'posts': posts,
        'categories': categories,
        'products': products,
        'carbon_ranking': ranking_list,
        'cart_total': request.session.get('cart_total', 0),
        'selected_category': int(category_id) if category_id else None,
    }
    return render(request, 'app1/community.html', context)

def dashboard(request):
    return render(request, 'app1/dashboard.html')

def view_cart(request):
    return render(request, 'app1/cart.html')

def product_detail(request, pk):
    return render(request, 'app1/product_detail.html')

def blog_detail(request, pk):
    return render(request, 'app1/blog_detail.html')

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
    paginate_by = 12  # Add pagination

    def get_queryset(self):
        # Start with base queryset
        queryset = super().get_queryset()

        # Search query
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query)
            )

        # Sustainability filter
        sustainable_filter = self.request.GET.get('sustainable', False)
        if sustainable_filter:
            queryset = queryset.filter(is_sustainable=True)

        # Price range filter
        try:
            min_price = float(self.request.GET.get('min_price', 0))
            max_price = float(self.request.GET.get('max_price', float('inf')))
            
            # Filter by price range if both are provided
            if min_price > 0 or max_price < float('inf'):
                queryset = queryset.filter(
                    price__gte=min_price,
                    price__lte=max_price
                )
        except (ValueError, TypeError):
            # If price conversion fails, ignore price filtering
            pass

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Pass filter parameters to template
        context['query'] = self.request.GET.get('q', '')
        context['sustainable_filter'] = self.request.GET.get('sustainable', False)
        
        # Price range parameters
        context['min_price'] = self.request.GET.get('min_price', '')
        context['max_price'] = self.request.GET.get('max_price', '')

        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'app1/product_detail.html'
    context_object_name = 'product'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
    total_products = Product.objects.count()
    sustainable_products = Product.objects.filter(is_sustainable=True).count()
    total_carbon_saved = CarbonFootprint.objects.aggregate(total=Sum('carbon_saved_kg'))['total'] or 0.0
    average_price = Product.objects.aggregate(avg_price=Avg('price'))['avg_price'] or 0.0
    average_price = round(average_price, 2)
    products_per_seller = User.objects.annotate(
        product_count=Count('products')
    ).values('username', 'product_count').filter(product_count__gt=0)
    total_users = User.objects.count()
    thirty_days_ago = datetime.now() - timedelta(days=30)
    active_users = User.objects.filter(last_login__gte=thirty_days_ago).count()
    active_percentage = round((active_users / total_users * 100) if total_users > 0 else 0, 1)
    recent_users = User.objects.order_by('-last_login')[:5]
    carbon_equivalent_trees = round(total_carbon_saved / 20)
    carbon_equivalent_cars = round(total_carbon_saved / 4700)
    products_per_user = round(Product.objects.count() / total_users, 1) if total_users > 0 else 0
    total_orders = 120
    total_revenue = 4500.00
    recent_orders = [
        {'id': 1, 'user': User.objects.first() or {'username': 'user1'}, 'total_amount': 150.00, 'created_at': datetime.now(), 'status': 'completed'},
        {'id': 2, 'user': User.objects.first() or {'username': 'user2'}, 'total_amount': 200.00, 'created_at': datetime.now() - timedelta(days=1), 'status': 'pending'},
        {'id': 3, 'user': User.objects.first() or {'username': 'user3'}, 'total_amount': 80.00, 'created_at': datetime.now() - timedelta(days=2), 'status': 'completed'},
    ]
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
        'average_rating': None,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
        'top_products': top_products,
    }
    return render(request, 'app1/dashboard.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def user_management(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'app1/user_management.html', {'users': users})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def edit_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
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
        order = Order.objects.create(user=request.user, total=total)
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['product'].price
            )
        Payment.objects.create(order=order, amount=total)
        del request.session['cart']
        return redirect('app1:payment', order_id=order.id)
    context = {
        'cart_items': cart_items,
        'total': total
    }
    return render(request, 'app1/checkout.html', context)

@login_required
def payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    payment, created = Payment.objects.get_or_create(order=order, defaults={'amount': order.total})

    # Handle receipt upload
    if request.method == 'POST':
        receipt = request.FILES.get('receipt')
        if receipt:
            payment.receipt = receipt
            payment.status = 'PENDING'
            payment.save()
            order.status = 'PAID'
            order.save()
            logger.info(f"Receipt uploaded for payment {payment.id}")
            messages.success(request, "Receipt uploaded successfully!")

    # Generate PromptPay QR code
    promptpay_id = "0801857971"  # Mobile number
    amount = f"{order.total:.2f}"  # Ensure two decimal places
    currency = "THB"
    qr_code_dir = os.path.join(settings.MEDIA_ROOT, 'QRCODE')
    try:
        if not os.path.exists(qr_code_dir):
            os.makedirs(qr_code_dir)
        qr_filename = f"qrcode_{promptpay_id}_{currency}_{datetime.now().strftime('%Y%m%d%H%M%S')}.PNG"
        qr_path = os.path.join(qr_code_dir, qr_filename)
        qr_success = qr_code(
            account=promptpay_id,
            one_time=True,
            path_qr_code=qr_path,
            country="TH",
            money=amount,
            currency=currency
        )
        if qr_success:
            logger.debug(f"QR code generated at {qr_path} for amount {amount}")
        else:
            logger.error(f"Failed to generate QR code for order {order.id}")
            messages.error(request, "Failed to generate QR code. Please try again.")
    except Exception as e:
        logger.error(f"QR code generation failed for order {order.id}: {str(e)}")
        messages.error(request, "Error generating QR code. Please contact support.")
        qr_filename = None

    # Relative path for template
    qr_url = os.path.join(settings.MEDIA_URL, 'QRCODE', qr_filename) if qr_filename else None

    context = {
        'order': order,
        'payment': payment,
        'qr_code_url': qr_url,
    }
    return render(request, 'app1/payment.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def payment_status(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Payment.STATUS_CHOICES).keys():
            old_status = payment.status
            payment.status = new_status
            payment.save()
            logger.info(f"Payment {payment.id} status changed from {old_status} to {new_status} by {request.user.username}")
            messages.success(request, f"Payment status updated to {new_status}.")
            # Sync order status if payment is APPROVED or VERIFIED
            if new_status in ['APPROVED', 'VERIFIED']:
                payment.order.status = 'PAID'
                payment.order.save()
            elif new_status == 'REJECTED':
                payment.order.status = 'CANCELLED'
                payment.order.save()
        else:
            logger.error(f"Invalid status {new_status} attempted for payment {payment.id}")
            messages.error(request, "Invalid status selected.")
        return redirect('app1:payment_status', payment_id=payment.id)

    context = {
        'payment': payment,
    }
    return render(request, 'app1/payment_status.html', context)

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'app1/order_history.html', {'orders': orders})

@login_required
def order_history_main(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'app1/order_history_main.html', {'orders': orders})

@login_required
def order_view_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)
    return render(request, 'app1/order_view_detail.html', {'order': order, 'order_items': order_items})

@login_required
def pending_payments(request):
    orders = Order.objects.filter(
        user=request.user,
        status='PENDING',
        payment__status='PENDING'
    ).order_by('-order_date')
    return render(request, 'app1/pending_payments.html', {'orders': orders})

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user, status='PENDING', payment__status='PENDING')
    if request.method == 'POST':
        order.delete()
        messages.success(request, f'Order #{order_id} has been cancelled.')
        return redirect('app1:pending_payments')
    return redirect('app1:pending_payments')

def blog(request):
    articles = Blog.objects.all()
    context = {
        'articles': articles
    }
    return render(request, 'app1/blog.html', context)

def blog_detail(request, article_id):
    article = get_object_or_404(Blog, id=article_id)
    context = {'article': article}
    return render(request, 'app1/blog_details.html', context)

@api_view(['GET', 'POST'])
@login_required
def get_community_posts(request):
    if request.method == 'GET':
        try:
            posts = CommunityPost.objects.select_related('user', 'category').all().order_by('-created_at')
            data = [{
                'id': post.id,
                'username': post.user.username if post.user else 'Anonymous',
                'title': post.title,
                'content': post.content,
                'timestamp': post.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'likes': post.likes.count(),
                'comments': post.comments.count(),
                'category': post.category.name if post.category else 'Uncategorized',
                'image': post.image.url if post.image else None,
                'is_owner': post.user == request.user
            } for post in posts]
            return Response(data)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
    elif request.method == 'POST':
        try:
            data = request.data
            title = data.get('title')
            content = data.get('content')
            category_name = data.get('category')
            image = request.FILES.get('image')
            if not title or not content or not category_name:
                return Response({'error': 'Title, content, and category are required'}, status=400)
            try:
                category = CommunityCategory.objects.get(name__iexact=category_name.strip())
            except CommunityCategory.DoesNotExist:
                available_categories = list(CommunityCategory.objects.values_list('name', flat=True))
                return Response({
                    'error': f'Invalid category "{category_name}". Available categories: {available_categories}'
                }, status=400)
            post = CommunityPost.objects.create(
                user=request.user,
                title=title,
                content=content,
                category=category,
                image=image
            )
            return Response({
                'id': post.id,
                'username': post.user.username,
                'title': post.title,
                'content': post.content,
                'timestamp': post.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'likes': post.likes.count(),
                'comments': post.comments.count(),
                'category': post.category.name,
                'image': post.image.url if post.image else None,
                'is_owner': True
            }, status=201)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@login_required
def create_review(request):
    try:
        data = request.data
        product_id = data.get('product_id')
        rating = data.get('rating')
        content = data.get('content')
        if not all([product_id, rating, content]):
            return Response({'error': 'Product ID, rating and content are required'}, status=400)
        product = get_object_or_404(Product, id=product_id)
        existing_review = Review.objects.filter(user=request.user, product=product).first()
        if existing_review:
            return Response({'error': 'You have already reviewed this product'}, status=400)
        review = Review.objects.create(
            user=request.user,
            product=product,
            rating=rating,
            content=content
        )
        return Response({
            'status': 'success',
            'review_id': review.id,
            'rating': review.rating,
            'content': review.content,
            'created_at': review.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }, status=201)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def get_product_reviews(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product, is_active=True).order_by('-created_at')
    data = [{
        'id': review.id,
        'user': {
            'username': review.user.username,
            'profile_photo': review.user.profile.profile_photo.url if hasattr(review.user, 'profile') and review.user.profile.profile_photo else None
        },
        'rating': review.rating,
        'content': review.content,
        'created_at': review.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'is_owner': review.user == request.user
    } for review in reviews]
    return Response(data)

@login_required
@require_POST
def like_post(request):
    data = json.loads(request.body)
    post_id = data.get('post_id')
    if not post_id:
        return JsonResponse({'error': 'Post ID is required'}, status=400)
    post = get_object_or_404(CommunityPost, id=post_id)
    like, created = PostLike.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
        action = 'unliked'
    else:
        action = 'liked'
    return JsonResponse({
        'status': 'success',
        'action': action,
        'likes_count': getattr(post, 'likes_count', 0)
    })

@login_required
@require_POST
def add_comment(request):
    data = json.loads(request.body)
    post_id = data.get('post_id')
    comment_text = data.get('comment')
    if not post_id or not comment_text or not comment_text.strip():
        return JsonResponse({'error': 'Post ID and comment text are required'}, status=400)
    post = get_object_or_404(CommunityPost, id=post_id)
    comment = Comment.objects.create(
        user=request.user,
        post=post,
        content=comment_text
    )
    return JsonResponse({
        'status': 'success',
        'comment_id': comment.id,
        'user': request.user.username,
        'content': comment.content,
        'created_at': comment.created_at.strftime('%b %d, %Y, %I:%M %p'),
        'comments_count': getattr(post, 'comments_count', 0)
    })

@api_view(['GET'])
@login_required
def get_comments(request, post_id):
    try:
        comments = Comment.objects.filter(post_id=post_id).select_related('user').order_by('-created_at')
        data = [{
            'id': comment.id,
            'content': comment.content,
            'user': {'username': comment.user.username},
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'is_owner': comment.user == request.user
        } for comment in comments]
        return Response(data)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@login_required
@require_POST
def delete_comment(request):
    data = json.loads(request.body)
    comment_id = data.get('comment_id')
    if not comment_id:
        return JsonResponse({'error': 'Comment ID is required'}, status=400)
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.user != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    post = comment.post
    comment.delete()
    return JsonResponse({
        'status': 'success',
        'comments_count': getattr(post, 'comments_count', 0)
    })

@login_required
@require_POST
def create_post(request):
    data = json.loads(request.body)
    title = data.get('title')
    content = data.get('content')
    category_id = data.get('category_id')
    if not title or not content or not category_id:
        return JsonResponse({
            'error': 'Title, content, and category are required'
        }, status=400)
    category = get_object_or_404(CommunityCategory, id=category_id)
    post = CommunityPost.objects.create(
        user=request.user,
        title=title,
        content=content,
        category=category
    )
    return JsonResponse({
        'status': 'success',
        'post_id': post.id,
        'title': post.title,
        'created_at': post.created_at.strftime('%b %d, %Y, %I:%M %p')
    })

@login_required
@require_POST
def delete_post(request):
    data = json.loads(request.body)
    post_id = data.get('post_id')
    if not post_id:
        return JsonResponse({'error': 'Post ID is required'}, status=400)
    post = get_object_or_404(CommunityPost, id=post_id)
    if post.user != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    post.delete()
    return JsonResponse({
        'status': 'success'
    })

@login_required
def get_post_details(request, post_id):
    post = get_object_or_404(CommunityPost, id=post_id)
    user_liked = PostLike.objects.filter(user=request.user, post=post).exists()
    comments = Comment.objects.filter(post=post).order_by('-created_at')
    comments_data = [{
        'id': comment.id,
        'user': comment.user.username,
        'content': comment.content,
        'created_at': comment.created_at.strftime('%b %d, %Y, %I:%M %p'),
        'is_owner': comment.user == request.user
    } for comment in comments]
    return JsonResponse({
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'user': post.user.username,
        'created_at': post.created_at.strftime('%b %d, %Y, %I:%M %p'),
        'likes_count': getattr(post, 'likes_count', 0),
        'comments_count': getattr(post, 'comments_count', 0),
        'user_liked': user_liked,
        'is_owner': post.user == request.user,
        'category': {
            'id': post.category.id,
            'name': post.category.name
        },
        'comments': comments_data
    })

@api_view(['GET'])
def get_categories(request):
    categories = CommunityCategory.objects.all()
    data = [{
        'id': cat.id,
        'name': cat.name,
        'description': cat.description
    } for cat in categories]
    return Response(data)

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
        wishlist = request.session.get('wishlist', [])
        if product_id not in wishlist:
            wishlist.append(product_id)
            request.session['wishlist'] = wishlist
            return JsonResponse({'status': 'success', 'message': f'Added {product.name} to wishlist!'})
        else:
            return JsonResponse({'status': 'info', 'message': f'{product.name} is already in your wishlist!'})
    elif request.method == 'GET':
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
    wishlist = request.session.get('wishlist', [])
    products = Product.objects.filter(id__in=wishlist)
    context = {
        'wishlist': products,
    }
    return render(request, 'app1/wishlist.html', context)

def about(request):
    context = {
        'page_title': 'About Us - Treevaq',
        'site_name': 'Treevaq',
    }
    return render(request, 'app1/about.html', context)


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
    

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import logging
from . import chatbot_utils

logger = logging.getLogger(__name__)

# Load model when Django starts - this will happen only once
try:
    model, tokenizer = chatbot_utils.load_model()
    logger.info("Chatbot model loaded on server startup")
except Exception as e:
    logger.error(f"Failed to load model on startup: {str(e)}")

@csrf_exempt
@require_POST
def chatbot_api(request):
    """API endpoint to handle chatbot requests"""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
        
        if not user_message.strip():
            return JsonResponse({'status': 'error', 'error': 'Message cannot be empty'}, status=400)
        
        response = chatbot_utils.generate_response(
            prompt=user_message,
            max_length=150,
            temperature=0.7
        )
        
        return JsonResponse({'status': 'success', 'response': response})
    
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'error': 'Invalid JSON data'}, status=400)
    
    except Exception as e:
        logger.error(f"Error in chatbot API: {str(e)}")
        return JsonResponse({'status': 'error', 'error': 'An error occurred while processing your request'}, status=500)