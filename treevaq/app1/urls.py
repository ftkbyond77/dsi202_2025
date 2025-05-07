# from django.urls import path
# from . import views

# app_name = 'app1'  # Namespace should match the app name

# urlpatterns = [
#     path('', views.home, name='home'),
#     path('products/', views.ProductListView.as_view(), name='product_list'),
#     path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
# ]

# from django.urls import path
# from . import views

# app_name = 'app1'

# urlpatterns = [
#     # Template URLs
#     path('', views.home, name='home'),
#     path('products/', views.ProductListView.as_view(), name='product_list'),
#     path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
#     # API URLs
#     path('api/products/', views.ProductListCreateAPIView.as_view(), name='api_product_list_create'),
#     path('api/products/<int:pk>/', views.ProductRetrieveUpdateAPIView.as_view(), name='api_product_retrieve_update'),
# ]

from django.urls import path
from . import views

app_name = 'app1'

urlpatterns = [
    # Template URLs
    path('', views.home, name='home'),
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    path('user-management/', views.user_management, name='user_management'),
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('activate-user/<int:user_id>/', views.activate_user, name='activate_user'),
    path('deactivate-user/<int:user_id>/', views.deactivate_user, name='deactivate_user'),
    
    path('cart/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('blog/', views.blog, name='blog'),
    path('blog/<int:article_id>/', views.blog_detail, name='blog_detail'),
    path('community/', views.community, name='community'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('add-to-wishlist/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove-from-wishlist/', views.remove_from_wishlist, name='remove_from_wishlist'),
    
    path('signup/', views.SignupView.as_view(), name='signup'),
    
    # API URLs
    path('api/products/', views.ProductListCreateAPIView.as_view(), name='api_product_list_create'),
    path('api/products/<int:pk>/', views.ProductRetrieveUpdateAPIView.as_view(), name='api_product_retrieve_update'),
]