from rest_framework import viewsets, status ,generics
from rest_framework.decorators import action, api_view 
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Sum, Count
from decimal import Decimal
from datetime import timedelta
import uuid
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import UserSerializer
from .models import MenuItem, Order, OrderItem, Payment
from .serializers import (
    MenuItemSerializer, OrderSerializer, OrderCreateSerializer,
    OrderUpdateSerializer, PaymentSerializer, PaymentCreateSerializer
)

# ---------------- MENU ----------------
class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get available menu items"""
        items = self.queryset.filter(is_available=True)
        return Response(self.get_serializer(items, many=True).data)

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get items grouped by category"""
        data = {}
        for cat, _ in MenuItem.CATEGORY_CHOICES:
            data[cat] = MenuItemSerializer(MenuItem.objects.filter(category=cat), many=True).data
        return Response(data)


# ---------------- ORDERS ----------------
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer
    lookup_field = 'order_id'  # keep this if frontend uses order_id in URL

    def create(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order_id = f"ORD-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        items_data = serializer.validated_data.pop('items')
        subtotal = Decimal('0')

        for item in items_data:
            menu_item = get_object_or_404(MenuItem, id=item['menu_item_id'])
            subtotal += menu_item.price * item['quantity']

        tax = subtotal * Decimal('0.05')
        delivery = Decimal('0') if subtotal > 500 else Decimal('50')

        order = Order.objects.create(
            order_id=order_id,
            subtotal=subtotal,
            tax=tax,
            delivery_charge=delivery,
            total_amount=subtotal + tax + delivery,
            **serializer.validated_data
        )

        for item in items_data:
            menu_item = get_object_or_404(MenuItem, id=item['menu_item_id'])
            OrderItem.objects.create(order=order, menu_item=menu_item, quantity=item['quantity'], price=menu_item.price)

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'])
    def update_status(self, request, order_id=None):
        order = self.get_object()
        new_status = request.data.get("status")
        if not new_status:
            return Response({"error": "Missing 'status' field"}, status=status.HTTP_400_BAD_REQUEST)
        order.status = new_status
        order.save()
        return Response({"message": f"Order {order.order_id} updated to {new_status}"}, status=status.HTTP_200_OK)



# ---------------- PAYMENTS ----------------
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    @action(detail=False, methods=['post'])
    def process_payment(self, request):
        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = get_object_or_404(Order, id=serializer.validated_data['order_id'])
        payment = Payment.objects.create(
            order=order,
            transaction_id=serializer.validated_data['transaction_id'],
            amount=serializer.validated_data['amount'],
            payment_method=serializer.validated_data['payment_method'],
            status='completed'
        )

        order.payment_status = 'completed'
        order.status = 'confirmed'
        order.save()

        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def by_order(self, request):
        order_id = request.query_params.get('order_id')
        if not order_id:
            return Response({'detail': 'Missing order_id'}, status=400)
        payment = get_object_or_404(Payment, order_id=order_id)
        return Response(PaymentSerializer(payment).data)


# ---------------- ADMIN ----------------
@api_view(['GET'])
def admin_dashboard(request):
    today = timezone.now().date()
    total_orders = Order.objects.count()
    today_orders = Order.objects.filter(created_at__date=today).count()
    total_revenue = Order.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    popular_items = OrderItem.objects.values('menu_item__name').annotate(count=Count('id')).order_by('-count')[:5]

    return Response({
        'total_orders': total_orders,
        'today_orders': today_orders,
        'total_revenue': float(total_revenue),
        'popular_items': list(popular_items),
    })


@api_view(['GET'])
def admin_orders(request):
    status_filter = request.query_params.get('status')
    date_filter = request.query_params.get('date')
    orders = Order.objects.all()
    if status_filter:
        orders = orders.filter(status=status_filter)
    if date_filter:
        orders = orders.filter(created_at__date=date_filter)
    return Response(OrderSerializer(orders, many=True).data)


@api_view(['GET'])
def admin_menu_stats(request):
    total_items = MenuItem.objects.count()
    available_items = MenuItem.objects.filter(is_available=True).count()
    unavailable_items = total_items - available_items
    by_category = MenuItem.objects.values('category').annotate(count=Count('id'))
    return Response({
        'total_items': total_items,
        'available_items': available_items,
        'unavailable_items': unavailable_items,
        'items_by_category': list(by_category),
    })

class UpdateOrderStatusView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        new_status = request.data.get("status")
        if not new_status:
            return Response({"error": "Missing status field"}, status=status.HTTP_400_BAD_REQUEST)
        order.status = new_status
        order.save()
        return Response({"message": f"Order {order.id} updated to {new_status}"}, status=status.HTTP_200_OK)

@api_view(['GET'])
def track_order(request, order_id):
    try:
        order = Order.objects.get(order_id=order_id)
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Order.DoesNotExist:
        return Response({"detail": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PATCH'])
def update_order_status(request, order_id):
    try:
        order = Order.objects.get(order_id=order_id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get('status')
    if not new_status:
        return Response({'error': 'Status not provided'}, status=status.HTTP_400_BAD_REQUEST)

    order.status = new_status
    order.save()
    return Response({
        'message': 'Status updated successfully',
        'order_id': order.order_id,
        'new_status': order.status
    }, status=status.HTTP_200_OK)




# Token generator function
def get_token_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token)
    }


# Registration View
class RegistrationView(APIView):
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        # Validation checks
        if not username or not password:
            return Response({"error": "Username and password are required"},
                            status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already taken"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Generate JWT tokens
        token = get_token_for_user(user)

        return Response({
            "user": UserSerializer(user).data,
            "token": token
        }, status=status.HTTP_201_CREATED)


# Login View
class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        # Check if credentials are provided
        if not username or not password:
            return Response({"error": "Username and password are required"},
                            status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)

        if not user:
            return Response({"error": "Invalid credentials"},
                            status=status.HTTP_401_UNAUTHORIZED)

        # Generate JWT tokens
        token = get_token_for_user(user)

        return Response({
            "user": UserSerializer(user).data,
            "token": token
        }, status=status.HTTP_200_OK)