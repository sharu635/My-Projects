from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Category, Product, Cart, CartItem, Order, OrderItem
from django.db.models import Q

def home(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )
        
    # Filter by category
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)
        
    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'current_category': category_slug
    }
    return render(request, 'home.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product_detail.html', {'product': product})

# Authentication
def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful. Welcome!')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            
            # Redirect to next if exists
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')

# Cart
def get_or_create_cart(user):
    cart, created = Cart.objects.get_or_create(user=user)
    return cart

@login_required
def cart_view(request):
    cart = get_or_create_cart(request.user)
    items = cart.items.all()
    subtotal = sum(item.get_total_price() for item in items)
    return render(request, 'cart.html', {'items': items, 'subtotal': subtotal})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    if product.stock_quantity < quantity:
        messages.error(request, f'Only {product.stock_quantity} left in stock.')
        return redirect('product_detail', product_id=product.id)
        
    cart = get_or_create_cart(request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
        
    cart_item.save()
    messages.success(request, f'{product.name} added to cart.')
    return redirect('cart')

@login_required
def update_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0:
        if item.product.stock_quantity < quantity:
            messages.error(request, f'Only {item.product.stock_quantity} left in stock.')
        else:
            item.quantity = quantity
            item.save()
            messages.success(request, 'Cart updated.')
    else:
        item.delete()
        
    return redirect('cart')

@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('cart')

# Checkout
@login_required
def checkout(request):
    cart = get_or_create_cart(request.user)
    items = cart.items.all()
    
    if not items:
        messages.error(request, 'Your cart is empty.')
        return redirect('home')
        
    subtotal = sum(item.get_total_price() for item in items)
    
    if request.method == 'POST':
        address = request.POST.get('address')
        if not address:
            messages.error(request, 'Please provide a shipping address.')
            return render(request, 'checkout.html', {'items': items, 'subtotal': subtotal})
            
        # Create Order
        order = Order.objects.create(
            user=request.user,
            total_price=subtotal,
            shipping_address=address
        )
        
        # Create Order Items and update stock
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            # Reduce stock
            item.product.stock_quantity -= item.quantity
            item.product.save()
            
        # Clear Cart
        cart.items.all().delete()
        
        messages.success(request, 'Order placed successfully!')
        return redirect('order_success', order_id=order.id)
        
    return render(request, 'checkout.html', {'items': items, 'subtotal': subtotal})

@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_success.html', {'order': order})
