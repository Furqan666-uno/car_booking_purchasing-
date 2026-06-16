from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import uuid

class User(AbstractUser):
    ROLE_CHOICE= (
        ('ADMIN', 'Admin'),
        ('STAFF', 'Staff'),
        ('CUSTOMER', 'Customer'),
        ('SELLER', 'Seller'),
    )
    id= models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username= models.CharField(max_length=100, unique=True)
    photo= models.ImageField(upload_to='users/photo/', null=True, blank=True)
    email= models.EmailField(unique=True)
    phone_no= models.CharField(max_length=12)
    role= models.CharField(max_length=10, choices=ROLE_CHOICE, default='CUSTOMER')
    is_online= models.BooleanField(default=False)

    USERNAME_FIELD= 'email' # while creating superuser, use email in place of username 
    REQUIRED_FIELDS= ['username', 'phone_no'] # beside email it allows superuser to ask for these as well

    def __str__(self):
        return f'Username:{self.username} Email:{self.email}'


class Car(models.Model):
    FUEL_CHOICE= (
        ('PETROL', 'Petrol'),
        ('DIESEL', 'Diesel'),
        ('ELECTRIC', 'Electric'),
    )
    TRANSMISSION_CHOICE= (
        ('AUTOMATIC', 'Automatic'),
        ('MANUAL', 'Manual'),
    )
    LISTING_CHOICE= (
        ('RENT', 'Rent'),
        ('SELL', 'Sell'),
        ('BOTH', 'Rent & Sale'),
    )
    id= models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cars')
    car_model= models.CharField(max_length=50)
    brand= models.CharField(max_length=50)
    release_year= models.PositiveIntegerField()
    fuel_type= models.CharField(max_length=20, choices=FUEL_CHOICE)
    transmission_type= models.CharField(max_length=20, choices=TRANSMISSION_CHOICE)
    seats= models.PositiveIntegerField()
    listing_type= models.CharField(max_length=30, choices=LISTING_CHOICE, default='RENT')
    renting_price= models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    selling_price= models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    available_for_rent= models.BooleanField(default=True)
    available_for_sale= models.BooleanField(default=False)
    created_at= models.DateTimeField(auto_now_add=True)
    is_available= models.BooleanField(default=True)

    def __str__(self):
        return f'{self.brand} {self.car_model} is available for {self.listing_type}'
    

class CarImage(models.Model): # seperate class for image to have multiple photos for each car
    id= models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    car= models.ForeignKey(Car, on_delete=models.CASCADE, related_name='car_images')
    image= models.ImageField(upload_to='car/images/')
    uploaded_at= models.DateTimeField(auto_now_add=True)
    

class Booking(models.Model):
    BOOKING_STATUS= (
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
    )   
    id= models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    car= models.ForeignKey(Car, on_delete=models.CASCADE, related_name='bookings')
    pickup_date= models.DateField()
    return_date= models.DateField()
    price= models.DecimalField(max_digits=10, decimal_places=2)
    status= models.CharField(max_length=20, choices=BOOKING_STATUS, default='PENDING')
    created_at= models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.car.brand} {self.car.car_model} is {self.status}'
    

class Purchase(models.Model):
    PURCHASE_STATUS= (
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
    )   
    id= models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    buyer= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='purchases')
    car= models.ForeignKey(Car, on_delete=models.CASCADE, related_name='purchase')
    price= models.DecimalField(max_digits=10, decimal_places=2)
    status= models.CharField(max_length=20, choices=PURCHASE_STATUS, default='PENDING')
    purchased_at= models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.buyer.username} bought the {self.car.brand} {self.car.car_model}'
    

class Payment(models.Model):
    PAYMENT_METHOD= (
        ('CASH', 'Cash'),
        ('CARD', 'Card'),
        ('UPI', 'UPI'),
        ('NET BANKING', 'Net Banking'),
    )
    PAYMENT_STATUS= (
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
    )
    id= models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    booking= models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    purchase= models.ForeignKey(Purchase, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    amount= models.DecimalField(max_digits=10, decimal_places=2)
    payment_method= models.CharField(max_length=30, choices=PAYMENT_METHOD)
    payment_status= models.CharField(max_length=30, choices=PAYMENT_STATUS, default='PENDING')
    transaction_id= models.CharField(max_length=100, unique=True)
    paid_at= models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.payment_status}'
    

class Conversation(models.Model):
    id= models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    buyer= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='buyer_conversations')
    seller= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='seller_conversations')
    car= models.ForeignKey(Car, on_delete=models.CASCADE, related_name='conversations')
    created_at= models.DateTimeField(auto_now_add=True)

    class Meta: # to prevent users from creating muliple conversations for same car again n again
        unique_together= ['buyer', 'seller', 'car']

    def __str__(self):
        return f'{self.buyer.username} - {self.seller.username}'
    

class Message(models.Model):
    id= models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation= models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text= models.TextField()
    file= models.FileField(upload_to='chat/files/', blank=True, null=True)
    image= models.ImageField(upload_to='chat/images/', blank=True, null=True)
    is_read= models.BooleanField(default=False)
    created_at= models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender.username}'