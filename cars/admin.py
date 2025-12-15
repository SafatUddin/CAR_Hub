from django.contrib import admin
from .models import Car, Order, Notification, UserProfile, CarImage

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'buyer', 'car', 'total_price', 'status', 'get_optional_features', 'created_at']
    list_filter = ['status', 'has_warranty', 'has_dashcam', 'has_seatcovers', 'has_tinting']
    search_fields = ['buyer__username', 'car__make', 'car__model']
    
    def get_optional_features(self, obj):
        features = []
        if obj.has_warranty:
            features.append('Warranty')
        if obj.has_dashcam:
            features.append('Dashcam')
        if obj.has_seatcovers:
            features.append('Seat Covers')
        if obj.has_tinting:
            features.append('Tinting')
        return ', '.join(features) if features else 'None'
    get_optional_features.short_description = 'Optional Features'

admin.site.register(Car)
admin.site.register(Notification)
admin.site.register(UserProfile)
admin.site.register(CarImage)
