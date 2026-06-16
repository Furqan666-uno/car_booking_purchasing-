from django.urls import path
from .views import (
    RegistrationView, LoginView, profile_view, change_password_view, reset_password_view, forgot_password_view, 
    create_car_view, car_list_view, single_car_view, update_car_view, delete_car_view,
    upload_car_image_view, car_images_view, delete_car_images_view,
    create_booking_view, booking_history_view, cancel_booking_view,
    create_purchase_view, purchase_history_view, cancel_purchase_view,
    create_payment_view, payment_history_view, cancel_payment_view,
    seller_dashboard_view, staff_dashboard_view, admin_dashboard_view,
    create_conversation_view, conversation_message_view, send_message_view,
)

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', profile_view, name='profile'),
    path('change-password/', change_password_view, name='change-password'),
    path('forgot-password/', forgot_password_view, name='forgot-password'),
    path('reset-password/', reset_password_view, name='reset-password'),

    path('cars/', car_list_view, name='car-list'),
    path('cars/create/', create_car_view, name='create-car'),
    path('cars/<uuid:id>/', single_car_view, name='car-view'),
    path('cars/update/<uuid:id>/', update_car_view, name='update-car'),
    path('cars/delete/<uuid:id>/', delete_car_view, name='delete-car'),

    path('cars/<uuid:car_id>/upload-image/', upload_car_image_view, name='upload-car-image'),
    path('cars/<uuid:car_id>/car-images/', car_images_view, name='car-images'),
    path('cars/images/<uuid:image_id>/delete/', delete_car_images_view, name='delete-car-image'),

    path('bookings/create/', create_booking_view, name='create-booking'),
    path('bookings/history/', booking_history_view, name='booking-history'),
    path('bookings/cancel/<uuid:booking_id>/', cancel_booking_view, name='cancel-booking'),

    path('purchases/create/', create_purchase_view, name='create-purchase'),
    path('purchases/history/', purchase_history_view, name='purchase-history'),
    path('purchases/cancel/<uuid:purchase_id>/', cancel_purchase_view, name='cancel-purchase'),

    path('payments/create/', create_payment_view, name='create-payment'),
    path('payments/history/', payment_history_view, name='payment-history'),
    path('payments/cancel/<uuid:payment_id>/', cancel_payment_view, name='cancel-payment'),

    path('dashboard/seller/', seller_dashboard_view, name='seller-dashboard'),
    path('dashboard/staff/', staff_dashboard_view, name='staff-dashboard'),
    path('dashboard/admin/', admin_dashboard_view, name='admin-dashboard'),

    path('chat/create/<uuid:car_id>/', create_conversation_view, name='create-conversation'),
    path('chat/messages/<uuid:conversation_id>/', conversation_message_view, name='conversation-view'),
    path('chat/send/<uuid:conversation_id>/', send_message_view, name='send-conversation'),
]
