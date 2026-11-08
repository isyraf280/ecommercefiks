def cart_context(request):
    """Menghitung total kuantitas produk dalam keranjang belanja."""
    cart = request.session.get('cart', {})
    total_qty = sum(item.get('jumlah', 1) for item in cart.values())
    return {
        'cart_total_qty': total_qty,
        'cart_has_items': total_qty > 0,
    }

