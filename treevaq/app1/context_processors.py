def cart_total(request):
    cart = request.session.get('cart', {})
    total = sum(int(quantity) for quantity in cart.values()) if cart else 0
    return {'cart_total': total}