from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'app1'

urlpatterns = [
    # --- Home ---
    path('', views.home, name='home'),

    # --- Product ---
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('checkout/', views.checkout, name='checkout'),

    path('payment/<int:order_id>/', views.payment, name='payment'),
    path('order-history/', views.order_history, name='order_history'),
    # --- Wishlist ---
    path('wishlist/', views.wishlist, name='wishlist'),
    path('add-to-wishlist/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove-from-wishlist/', views.remove_from_wishlist, name='remove_from_wishlist'),

    # --- Blog ---
    path('blog/', views.blog, name='blog'),
    path('blog/<int:article_id>/', views.blog_detail, name='blog_detail'),

    # --- Community ---
    path('community/', views.community, name='community'),
    
    # --- User / Auth / Dashboard ---
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('account/', views.account_view, name='account'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('user-management/', views.user_management, name='user_management'),
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('activate-user/<int:user_id>/', views.activate_user, name='activate_user'),
    path('deactivate-user/<int:user_id>/', views.deactivate_user, name='deactivate_user'),

    # --- API: User ---
    path('api/user/profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('api/user/orders/', views.OrderHistoryView.as_view(), name='order_history'),
    path('api/user/change-password/', views.ChangePasswordView.as_view(), name='change_password'),

    # --- API: Products & Categories ---
    path('api/categories/', views.get_categories, name='get_categories'),
    path('api/products/', views.ProductListCreateAPIView.as_view(), name='product_list_create'),
    path('api/products/<int:pk>/', views.ProductRetrieveUpdateAPIView.as_view(), name='product_retrieve_update'),

    # --- API: Community ---
    path('api/community/posts/', views.get_community_posts, name='get_community_posts'),
    path('api/community/post/<int:post_id>/', views.get_post_details, name='get_post_details'),
    path('api/community/create/', views.create_post, name='create_post'),
    path('api/community/delete/', views.delete_post, name='delete_post'),
    path('api/community/like/', views.like_post, name='like_post'),
    path('api/community/comment/', views.add_comment, name='add_comment'),
    path('api/community/comment/delete/', views.delete_comment, name='delete_comment'),
    path('api/community/comments/<int:post_id>/', views.get_comments, name='get_comments'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)