from rest_framework import serializers
from .models import MenuItem, Order, OrderItem, Payment, User

# ---------- MENU ITEMS ----------
class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


# ---------- ORDER ITEMS ----------
class OrderItemSerializer(serializers.ModelSerializer):
    menu_item = MenuItemSerializer(read_only=True)
    menu_item_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item', 'menu_item_id', 'quantity', 'price', 'created_at']


# ---------- ORDERS ----------
class OrderCreateItemSerializer(serializers.Serializer):
    menu_item_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class OrderCreateSerializer(serializers.Serializer):
    customer_name = serializers.CharField(max_length=100)
    table_number = serializers.IntegerField()
    phone_number = serializers.CharField(max_length=15)
    email = serializers.EmailField(required=False, allow_blank=True)
    payment_method = serializers.ChoiceField(choices=['online', 'cod'])
    special_instructions = serializers.CharField(required=False, allow_blank=True)
    items = OrderCreateItemSerializer(many=True)


class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status', 'payment_status']


# ---------- PAYMENTS ----------
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class PaymentCreateSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    transaction_id = serializers.CharField(max_length=100)
    payment_method = serializers.CharField(max_length=20)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields='__all__'