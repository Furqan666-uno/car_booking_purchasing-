from celery import shared_task
from .models import Booking, Purchase

@shared_task
def expire_booking(booking_id):
    try:
        booking= Booking.objects.get(id=booking_id)
        if booking.status=='PENDING': # if celery sees status is still pending after countdown(in booking view) 
            booking.status=='CANCELLED' # it cancels booking 
            booking.save()
            
    except Booking.DoesNotExist:
        pass 


@shared_task
def expire_purchase(purchase_id):
    try:
        purchase= Purchase.objects.get(id=purchase_id)
        if purchase.status=='PENDING': # if celery sees status is still pending after countdown(in booking view) 
            purchase.status=='CANCELLED' # it cancels booking 
            purchase.save()

            purchase.car.available_for_sale=True
            purchase.car.is_available=True
            purchase.car.save()

    except Purchase.DoesNotExist:
        pass 