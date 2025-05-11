from .models import Order

def cart_total(request):
    cart = request.session.get('cart', {})
    total = sum(int(quantity) for quantity in cart.values()) if cart else 0
    return {'cart_total': total}

def unpaid_orders(request):
    if request.user.is_authenticated:
        has_unpaid_orders = Order.objects.filter(
            user=request.user,
            status='PENDING',
            payment__status='PENDING'
        ).exists()
        return {'has_unpaid_orders': has_unpaid_orders}
    return {'has_unpaid_orders': False}