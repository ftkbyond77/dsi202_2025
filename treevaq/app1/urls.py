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
    path('dashboard/', views.dashboard, name='dashboard'),  # New dashboard route
    # API URLs
    path('api/products/', views.ProductListCreateAPIView.as_view(), name='api_product_list_create'),
    path('api/products/<int:pk>/', views.ProductRetrieveUpdateAPIView.as_view(), name='api_product_retrieve_update'),
]