from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.conf import settings

# Модель користувача
class CustomUser(AbstractUser):
    real_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)  # Додаємо відсутні поля
    address = models.CharField(max_length=255, blank=True, null=True)      # Додаємо відсутні поля

class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name="Назва продукту")
    description = models.TextField(verbose_name="Опис продукту", blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна продукту")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Зображення продукту")

    def __str__(self):
        return self.name

# Модель кошика
class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Кошик {self.user.username}"

    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())

# Модель елемента в кошику
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def get_total_price(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

# Модель замовлення
class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Нове'),
        ('processing', 'В обробці'),
        ('completed', 'Завершено'),
        ('canceled', 'Скасовано'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders', verbose_name="Користувач")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Статус замовлення")
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0,
        verbose_name="Загальна сума",
        validators=[MinValueValidator(0.01, message="Сума замовлення має бути більшою за 0.")]
    )

    def __str__(self):
        return f"Замовлення {self.id} - {self.user.username} - {self.status}"

# Модель елемента в замовленні
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Замовлення")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Продукт")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Кількість")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна")

    def __str__(self):
        return f"{self.quantity} x {self.product.name} у {self.order}"
