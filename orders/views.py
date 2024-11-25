from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, EditProfileForm
from .models import Product, Cart, CartItem, Order, OrderItem
from django.contrib.auth.forms import PasswordChangeForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import CommentForm
from rest_framework.viewsets import ModelViewSet
from .models import Product
from .serializers import ProductSerializer,OrderSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "This is a protected view"})

class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

def perform_create(self, serializer):
    serializer.save(user=self.request.user)

def get_text(request):
    data = {
        'message': 'Додайте хоч елемент один в кошик.'
    }
    return JsonResponse(data)

@csrf_exempt
def submit_comment(request):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            return JsonResponse({'status': 'success', 'message': 'Коментар збережений!'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Невірні дані.'})
    return JsonResponse({'status': 'error', 'message': 'Це не POST-запит.'})

# Головна сторінка
def index(request):
    return render(request, 'orders/index.html')

def about(request):
    return render(request, 'orders/about.html')

# Відображення списку продуктів
def product_list(request):
    products = Product.objects.all()
    return render(request, 'orders/product_list.html', {'products': products})

# Реєстрація користувача
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Реєстрація пройшла успішно!')
            return redirect('index')
        else:
            messages.error(request, 'Помилка реєстрації. Перевірте дані форми.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'orders/register.html', {'form': form})

# Перегляд профілю користувача
@login_required(login_url='login')
def user_profile(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at')

    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профіль успішно оновлено.')
            return redirect('user_profile')
        else:
            messages.error(request, 'Будь ласка, виправте помилки у формі.')
    else:
        form = EditProfileForm(instance=user)

    return render(request, 'orders/profile.html', {'form': form, 'orders': orders})

# Редагування профілю користувача
@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профіль успішно оновлено.')
            return redirect('user_profile')
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, 'orders/edit_profile.html', {'form': form})

# Зміна пароля
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Пароль успішно змінено.')
            return redirect('user_profile')
        else:
            messages.error(request, 'Будь ласка, виправте помилки.')
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'orders/change_password.html', {'form': form})

# Додавання продукту до кошика
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)


    quantity = request.POST.get('quantity', 1)

    try:
        quantity = int(quantity)
    except ValueError:
        quantity = 1  #

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    # Додаємо вказану кількість товару до існуючої
    cart_item.quantity += quantity
    cart_item.save()

    messages.success(request, f'{product.name} у кількості {quantity} шт. було додано до кошика.')
    return redirect('cart')

# Видалення елемента з кошика
@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, 'Елемент видалено з кошика.')
    return redirect('cart')

# Оновлення кількості елементів у кошику
@login_required
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if request.method == 'POST':
        new_quantity = request.POST.get('quantity', 1)
        cart_item.quantity = int(new_quantity)
        cart_item.save()
        messages.success(request, 'Кількість елементів оновлено.')
    return redirect('cart')

# Відображення кошика
@login_required(login_url='login')
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)


    cart_items = cart.items.all()
    total_price = cart.get_total_price()

    return render(request, 'orders/cart.html', {
        'cart': cart,
        'cart_items': cart_items,
        'total_price': total_price
    })

# Оформлення замовлення
import logging
from django.db import transaction

logger = logging.getLogger(__name__)

@login_required(login_url='login')
def order_form(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    if not cart.items.exists():
        messages.error(request, 'Ваш кошик порожній.')
        return redirect('product_list')

    if request.method == 'POST':
        try:
            with transaction.atomic():
                order = Order.objects.create(user=request.user, total_price=cart.get_total_price())
                order.save()
                logger.info(f"Order created: {order}")

                for item in cart.items.all():
                    order_item = OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.get_total_price()
                    )
                    logger.info(f"OrderItem created: {order_item}")

                cart.items.all().delete()

            messages.success(request, 'Замовлення успішно оформлено!')
            return redirect('order_success')
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            messages.error(request, f'Помилка оформлення замовлення: {e}')
            return redirect('cart')

    total_price = cart.get_total_price()
    return render(request, 'orders/order_form.html', {
        'cart': cart,
        'total_price': total_price
    })
# Сторінка успішного замовлення
@login_required
def order_success(request):
    return render(request, 'orders/order_success.html')
