from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class Car(models.Model):
    CAR_TYPES = (
        ('sedan', 'Sedan'),
        ('suv', 'SUV'),
        ('truck', 'Truck'),
        ('coupe', 'Coupe'),
    )
    
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    mileage = models.IntegerField()
    car_type = models.CharField(max_length=20, choices=CAR_TYPES)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, default='available') # available, sold
    approval_status = models.CharField(max_length=20, default='pending') # pending, approved, rejected
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Contact Info
    contact_email = models.EmailField(blank=True, null=True)
    contact_whatsapp = models.CharField(max_length=20, blank=True, null=True)
    
    # Registration Paper (nullable for existing records)
    registration_paper = models.FileField(upload_to='registration_papers/', blank=True, null=True)
    
    # Observer Pattern: Followers
    followers = models.ManyToManyField(User, related_name='followed_cars', blank=True)
    
    def __str__(self):
        return f"{self.year} {self.make} {self.model}"

class CarImage(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='car_images/')
    
    def __str__(self):
        return f"Image for {self.car}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Optional features
    has_warranty = models.BooleanField(default=False)
    has_dashcam = models.BooleanField(default=False)
    has_seatcovers = models.BooleanField(default=False)
    has_tinting = models.BooleanField(default=False)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=20, blank=True, null=True)
    payment_completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Order {self.id} - {self.car} by {self.buyer}"
    

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"Profile for {self.user.username}"

class PurchaseRequest(models.Model):
    """Handles purchase requests from buyers to sellers"""
    STATUS_CHOICES = [
        ('pending', 'Pending Seller Approval'),
        ('accepted', 'Accepted - Awaiting Payment'),
        ('payment_pending', 'Payment Pending'),
        ('paid', 'Paid - Transaction Complete'),
        ('rejected', 'Rejected by Seller'),
        ('cancelled', 'Cancelled by Buyer'),
    ]
    
    car = models.ForeignKey('Car', on_delete=models.CASCADE, related_name='purchase_requests')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_purchase_requests')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_sale_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True, help_text="Optional message to seller")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['car', 'buyer']  # One request per buyer per car
    
    def __str__(self):
        return f"{self.buyer.username} → {self.car}"


class Payment(models.Model):
    """Stores payment transaction details"""
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_banking', 'Mobile Banking'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    purchase_request = models.OneToOneField(PurchaseRequest, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Optional: Store card details (last 4 digits only for display)
    card_last4 = models.CharField(max_length=4, blank=True)
    cardholder_name = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment {self.transaction_id} - ${self.amount}"