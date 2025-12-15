from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('home/', views.home, name='home'),
    path('car/<int:car_id>/', views.car_detail, name='car_detail'),
    path('create/', views.create_car, name='create_car'),
    path('delete/<int:car_id>/', views.delete_car, name='delete_car'),
    path('update/<int:car_id>/', views.update_car, name='update_car'),
    path('notifications/', views.notifications, name='notifications'),
    path('api/notifications/count/', views.notification_count_api, name='notification_count_api'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('seller/<int:user_id>/', views.seller_profile, name='seller_profile'),
    path('buy/<int:car_id>/', views.buy_car, name='buy_car'),
    path('follow/<int:car_id>/', views.follow_car, name='follow_car'),
    path('update_status/<int:car_id>/', views.update_car_status, name='update_car_status'),
    path('accept_order/<int:order_id>/', views.accept_order, name='accept_order'),
    path('reject_order/<int:order_id>/', views.reject_order, name='reject_order'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path('mark_all_read/', views.mark_all_read, name='mark_all_read'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('approve-car/<int:car_id>/', views.approve_car, name='approve_car'),
    path('reject-car/<int:car_id>/', views.reject_car, name='reject_car'),
]
