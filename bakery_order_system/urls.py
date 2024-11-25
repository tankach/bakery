from orders import views  # Імпортуємо всі представлення з модуля orders
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.urls import path
from orders.views import user_profile, edit_profile, about
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include
from rest_framework.routers import DefaultRouter
from orders.views import ProductViewSet,OrderViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'order', OrderViewSet, basename='order')
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include(router.urls)),  # Додаємо всі маршрути API
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('about/', about, name='about'),
    path('products/', views.product_list, name='product_list'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('order/success/', views.order_success, name='order_success'),
    path('order/', views.order_form, name='order_form'),
    path('login/', auth_views.LoginView.as_view(template_name='orders/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='index'), name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', user_profile, name='user_profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('checkout/', views.order_form, name='checkout'),
    path('submit_comment/', views.submit_comment, name='submit_comment'),
    path('get_text/', views.get_text, name='get_text'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)