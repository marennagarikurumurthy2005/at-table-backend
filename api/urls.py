from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MenuItemViewSet, OrderViewSet, PaymentViewSet,
    admin_dashboard, admin_orders, admin_menu_stats,
    track_order, update_order_status,RegistrationView,LoginView
)

router = DefaultRouter()
router.register(r'menu-items', MenuItemViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('admin/dashboard/', admin_dashboard),
    path('admin/orders/', admin_orders),
    path('admin/menu-stats/', admin_menu_stats),

    # Customer order tracking and status update
    path('orders/<str:order_id>/track/', track_order, name='track_order'),
    path('orders/<str:order_id>/update_status/', update_order_status, name='update_order_status'),
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
]
