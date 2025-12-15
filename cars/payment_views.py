from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Order, Notification

@login_required
def initiate_payment(request, order_id):
    """Show payment options"""
    order = get_object_or_404(Order, id=order_id)
    
    # Check authorization
    if request.user != order.buyer:
        messages.error(request, "You are not authorized to pay for this order.")
        return redirect('home')
    
    # Check if already paid
    if order.status in ['paid', 'completed']: 
        messages.info(request, "This order has already been paid.")
        return redirect('profile')
    
    # Payment methods
    payment_methods = [
        {'value': 'bkash', 'name': 'bKash', 'icon': '📱', 'color': '#E2136E'},
        {'value': 'nagad', 'name': 'Nagad', 'icon': '📞', 'color': '#ED1C24'},
        {'value':  'rocket', 'name':  'Rocket', 'icon': '🚀', 'color': '#8B3A9C'},
        {'value': 'card', 'name': 'Credit/Debit Card', 'icon': '💳', 'color': '#4A90E2'},
    ]
    
    return render(request, 'cars/payment/initiate.html', {
        'order':  order,
        'payment_methods': payment_methods,
    })

@login_required
def process_payment(request, order_id):
    """Process mock payment"""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST': 
        payment_method = request.POST.get('payment_method')
        
        # Mock payment processing (instant success)
        order.status = 'paid'
        order.payment_method = payment_method
        order.payment_completed_at = timezone.now()
        order.save()
        
        # Notify seller
        Notification.objects.create(
            user=order.car.owner,
            message=f"💰 Payment Received!  {order.buyer.username} has paid ৳{order.total_price} for your {order.car.year} {order.car.make} {order.car.model}.You can now accept the order."
        )
        
        # Notify buyer
        Notification.objects.create(
            user=order.buyer,
            message=f"✅ Payment successful! You paid ৳{order.total_price} for {order.car.year} {order.car.make} {order.car.model}.Waiting for seller confirmation."
        )
        
        messages.success(request, f"Payment successful! ৳{order.total_price} paid via {payment_method}.")
        return redirect('payment_success', order_id=order.id)
    
    return redirect('initiate_payment', order_id=order_id)

@login_required
def payment_success(request, order_id):
    """Payment success page"""
    order = get_object_or_404(Order, id=order_id)
    
    return render(request, 'cars/payment/success.html', {
        'order': order,
    })