# from django.shortcuts import render
# from django.views.generic import ListView, DetailView
# from .models import Product
# from django.db.models import Q

# def home(request):
#     return render(request, 'app1/home.html')

# class ProductListView(ListView):
#     model = Product
#     template_name = 'app1/product_list.html'
#     context_object_name = 'products'

#     def get_queryset(self):
#         # Get the search query from the request's GET parameters
#         query = self.request.GET.get('q', '').strip()
#         queryset = super().get_queryset()

#         if query:
#             # Filter products where name or description contains the query (case-insensitive)
#             queryset = queryset.filter(
#                 Q(name__icontains=query) | Q(description__icontains=query)
#             )

#         return queryset

#     def get_context_data(self, **kwargs):
#         # Add the search query to the context so the template can display it
#         context = super().get_context_data(**kwargs)
#         context['query'] = self.request.GET.get('q', '')
#         return context

# class ProductDetailView(DetailView):
#     model = Product
#     template_name = 'app1/product_detail.html'
#     context_object_name = 'product'

# from django.shortcuts import render
# from django.views.generic import ListView, DetailView
# from .models import Product
# from django.db.models import Q
# from rest_framework import generics, permissions
# from .serializers import ProductSerializer

# # Existing Template Views
# def home(request):
#     return render(request, 'app1/home.html')

# class ProductListView(ListView):
#     model = Product
#     template_name = 'app1/product_list.html'
#     context_object_name = 'products'

#     def get_queryset(self):
#         query = self.request.GET.get('q', '').strip()
#         queryset = super().get_queryset()
#         if query:
#             queryset = queryset.filter(Q(name__icontains=query) | Q(description__icontains=query))
#         return queryset

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['query'] = self.request.GET.get('q', '')
#         return context

# class ProductDetailView(DetailView):
#     model = Product
#     template_name = 'app1/product_detail.html'
#     context_object_name = 'product'

# # API Views
# class ProductListCreateAPIView(generics.ListCreateAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#     permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # Read for all, create for authenticated users

# class ProductRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#     permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # Read for all, update for authenticated users

#     def perform_update(self, serializer):
#         # Ensure only the product's seller can update it
#         if self.request.user != serializer.instance.seller:
#             raise permissions.PermissionDenied("You can only update your own products.")
#         serializer.save()

from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Product, CarbonFootprint
from django.db.models import Q, Sum, Avg, Count
from django.contrib.auth.models import User
from rest_framework import generics, permissions
from .serializers import ProductSerializer
from django.contrib.auth.decorators import login_required


# Existing Template Views
def home(request):
    return render(request, 'app1/home.html')

class ProductListView(ListView):
    model = Product
    template_name = 'app1/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        queryset = super().get_queryset()
        if query:
            queryset = queryset.filter(Q(name__icontains=query) | Q(description__icontains=query))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'app1/product_detail.html'
    context_object_name = 'product'

@login_required
# New Dashboard View
def dashboard(request):
    # Total number of products
    total_products = Product.objects.count()

    # Number of sustainable products
    sustainable_products = Product.objects.filter(is_sustainable=True).count()

    # Total carbon saved (sum of carbon_saved_kg from CarbonFootprint)
    total_carbon_saved = CarbonFootprint.objects.aggregate(total=Sum('carbon_saved_kg'))['total'] or 0.0

    # Average product price
    average_price = Product.objects.aggregate(avg_price=Avg('price'))['avg_price'] or 0.0
    average_price = round(average_price, 2)  # Round to 2 decimal places

    # Number of products per seller
    products_per_seller = User.objects.annotate(
        product_count=Count('products')
    ).values('username', 'product_count').filter(product_count__gt=0)

    context = {
        'total_products': total_products,
        'sustainable_products': sustainable_products,
        'total_carbon_saved': total_carbon_saved,
        'average_price': average_price,
        'products_per_seller': products_per_seller,
    }
    return render(request, 'app1/dashboard.html', context)

# Existing API Views
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