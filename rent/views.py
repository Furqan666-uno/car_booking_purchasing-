from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from drf_spectacular.utils import extend_schema
# all the @extend_schema() written above all the views func() & classes are there only for preventing SwaggerUI errors. These are not mandatory & can be skipped if frontend for the project already is made. 

from .tasks import expire_booking, expire_purchase

import uuid
from django.db.models import Q, Sum
from django.db import transaction #transaction.atomics= use for connecting Booking/Purchasing and Payment, to make sure if payment later is cancelled or failed, the booking/purchasing of the car also gets cancelled 
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.core.paginator import Paginator

from .serializers import RegistrationSerializer, LoginSerializer, ProfileSerializer, ChangePasswordSerializer, ResetPasswordSerializer, ForgotPasswordSerializer, CarSerializer, CarImageSerializer, BookingSerializer, PurchaseSerializer, PaymentSerializer, ConversationSerializer, MessageSerializer
from .models import Car, CarImage, Booking, Purchase, Payment, Conversation, Message

User= get_user_model()


#-----------------------------------------Authentication/Authorization--------------------------------------------
@extend_schema(
    request=RegistrationSerializer,
    responses=RegistrationSerializer
)
class RegistrationView(APIView):
    def post(self, request):
        serializer= RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'User registered successfully.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@extend_schema(
    request=LoginSerializer
)
class LoginView(APIView):
    def post(self, request):
        serializer= LoginSerializer(data=request.data)
        if serializer.is_valid():
            user= serializer.validated_data['user']
            refresh= RefreshToken.for_user(user)
            return Response(
                {'message':'Login Successfully.', 'refresh':str(refresh), 'access':str(refresh.access_token),
                 'user': {'id': user.id, 
                          'email': user.email, 
                          'username':user.username, 
                          'role':user.role
                        }
                }, 
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=ProfileSerializer,
    responses=ProfileSerializer
)
@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated]) # only registered/authenticated users can view profile
def profile_view(request):
    if request.method=='GET':
        serializer= ProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method=='PUT': # PUT= complete update
        serializer= ProfileSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'Profile Updated successfully.', 'data':serializer.data}, status=status.HTTP_200_OK)
        return Response({'error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method=='PATCH': # PATCH= partial update
        serializer= ProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'Profile Updated successfully.', 'data':serializer.data}, status=status.HTTP_200_OK)
        return Response({'error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    

@extend_schema(
    request=ProfileSerializer,
    responses=ProfileSerializer
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    serializer= ChangePasswordSerializer(data=request.data, context={'user':request.user})
    if serializer.is_valid():
        new_password= serializer.validated_data['new_password']
        user= request.user
        user.set_password(new_password)
        user.save()
        return Response({'message':'Password updated successfully.'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=ProfileSerializer,
    responses=ProfileSerializer
)
@api_view(['POST'])
def forgot_password_view(request):
    serializer= ForgotPasswordSerializer(data=request.data)
    if serializer.is_valid():
        email= serializer.validated_data['email']
        user= User.objects.get(email=email)
        uid= urlsafe_base64_encode(force_bytes(user.id))
        token= PasswordResetTokenGenerator().make_token(user)
        reset_link= (f"http://127.0.0.1:8000/reset-password/{uid}/{token}/")
        send_mail(
            subject= 'Password reset request',
            message= f"Click the link to change password: \n {reset_link}",
            from_email=None,
            recipient_list=[email],
        )
        return Response({'message':'Reset link has been send to your email.'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=ProfileSerializer,
    responses=ProfileSerializer
)
@api_view(['POST'])
def reset_password_view(request, uidb64, token):
    try:
        uid= force_str(urlsafe_base64_decode(uidb64))
        user= User.objects.get(id=uid)
    except Exception:
        return Response({'error':'Invalid reset password link.'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not PasswordResetTokenGenerator().check_token(user, token):
        return Response({'error':'Token is invalid or expired.'}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer= ResetPasswordSerializer(data=request.data)
    if serializer.is_valid():
        new_password= serializer.validated_data['new_password']
        user.set_password(new_password)
        user.save()
        return Response({'message':'Password reset successfully.'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#---------------------------------------------Cars/CarImage Views------------------------------------------------
@extend_schema(
    request=CarSerializer,
    responses=CarSerializer
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_car_view(request):
    if request.user.role != 'SELLER':
        return Response({'error':'Only sellers are allowed to upload cars.'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer= CarSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(owner=request.user)
        return Response({'message':'Car added successfully.', 'data':serializer.data}, status=status.HTTP_201_CREATED)
    return Response({'error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    responses=CarSerializer(many=True),
    operation_id="list_cars"
)
@api_view(['GET'])
def car_list_view(request):
    cars= Car.objects.all()

    search= request.GET.get('search') # usr says api/car/?search=BMW, request.GET= search:BMW, GET.get=BMW
    if search:
        cars= cars.filter(Q(car_model__icontains=search) | Q(brand__icontains=search) | Q(fuel_type__icontains=search) | Q(transmission_type__icontains=search)) 
        # here '|' means OR. Q used for multiple model search
        # Also '~Q' means search if NOT, '&' means search1 AND search2

    allowed_ordering= ['renting_price', '-renting_price', 'selling_price', '-selling_price', 'created_at', '-created_at']
    ordering= request.GET.get('ordering') # if /api/car/?ordering, request.GET.get= ordering
    if ordering in allowed_ordering:
        cars= cars.order_by(ordering)
    else:
        cars= cars.order_by('-created_at')

    page= request.GET.get('page', 1) # if /api/cars/?page=1, here 1 will be by default
    paginator= Paginator(cars, 5) # 5 means it will show 5 datas per page
    cars= paginator.get_page(page) # bookings= 5 datas per page 

    serializer= CarSerializer(cars, many=True)
    return Response({'data':serializer.data, 'count':paginator.count, 'total_page':paginator.num_pages, 'current_page':cars.number}, status=status.HTTP_200_OK) 


@extend_schema(
    responses=CarSerializer(many=True),
    operation_id="list_cars"
)
@api_view(['GET'])
def single_car_view(request, id):
    try:
        car= Car.objects.get(id=id)
    except Car.DoesNotExist:
        return Response({'message':'Car not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer= CarSerializer(car)
    return Response({'data':serializer.data}, status=status.HTTP_200_OK)


@extend_schema(
    request=CarSerializer,
    responses=CarSerializer
)
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_car_view(request, id):
    try:
        car= Car.objects.get(id=id)
    except Car.DoesNotExist:
        return Response({'message':'Car not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method=='PUT':
        serializer= CarSerializer(car, data=request.data)
        if car.owner != request.user:
            return Response({'error':'You are not the owner of this car.'}, status=status.HTTP_403_FORBIDDEN)
        if request.user.role != 'SELLER':
            return Response({'error':'Only sellers are allowed to make changes.'}, status=status.HTTP_403_FORBIDDEN)
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'Car updated successfully.', 'data':serializer.data}, status=status.HTTP_200_OK)
        return Response({'error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
    if request.method=='PATCH':
        serializer= CarSerializer(car, data=request.data, partial=True)
        if car.owner != request.user:
            return Response({'error':'You are not the owner of this car.'}, status=status.HTTP_403_FORBIDDEN)
        if request.user.role != 'SELLER':
            return Response({'error':'Only sellers are allowed to make changes.'}, status=status.HTTP_403_FORBIDDEN)
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'Car updated successfully.', 'data':serializer.data}, status=status.HTTP_200_OK)
        return Response({'error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        

@extend_schema(
    request=None
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_car_view(request, id):
    try:
        car= Car.objects.get(id=id)
    except Car.DoesNotExist:
        return Response({'message':'Car not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.user.role != 'SELLER':
        return Response({'error':'Only sellers are allowed to make changes.'}, status=status.HTTP_403_FORBIDDEN)
    if car.owner != request.user:
        return Response({'error':'You are not the owner of this car.'}, status=status.HTTP_403_FORBIDDEN)
    car.delete()
    return Response({'message':'Car deleted successfully.'}, status=status.HTTP_200_OK)


# -----------------------------------------Car Image View---------------------------------------------------------
@extend_schema(
    request=CarImageSerializer,
    responses=CarImageSerializer
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_car_image_view(request, car_id): # car_id will be used in urls later
    try:
        car= Car.objects.get(id=car_id)
    except Car.DoesNotExist:
        return Response({'message':'Car not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer= CarImageSerializer(data=request.data)
    if car.owner != request.user:
       return Response({'error':'You are not the owner of this car.'}, status=status.HTTP_403_FORBIDDEN) 
    if request.user.role != 'SELLER':
        return Response({'error':'Only sellers are allowed to make changes.'}, status=status.HTTP_403_FORBIDDEN)
    if serializer.is_valid():
        serializer.save(car_image=car)
        return Response({'message':'Image uploaded successfully.', 'data':serializer.data}, status=status.HTTP_201_CREATED)
    return Response({'error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    

@extend_schema(
    request=CarImageSerializer,
    responses=CarImageSerializer(many=True)
)
@api_view(['GET'])
def car_images_view(request, car_id):
    try:
        cars= Car.objects.get(id=car_id)
    except Car.DoesNotExist:
        return Response({'error':'Car not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    images= cars.car_images.all() # bcz related_name='car_images' in CarImage model
    serializer= CarImageSerializer(images, many=True)
    return Response({'data':serializer.data}, status=status.HTTP_200_OK)

@extend_schema(
    request=None
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_car_images_view(request, image_id): # <image_id> will be the id in urls later
    try:
        images= CarImage.objects.get(id=image_id)
    except CarImage.DoesNotExist:
        return Response({'error':'Image not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    if images.car_images.owner != request.user:
        return Response({'error':'You are not the owner of this car.'}, status=status.HTTP_403_FORBIDDEN)
    if request.user.role != 'SELLER':
        return Response({'error':'Only sellers are allowed to make changes.'}, status=status.HTTP_403_FORBIDDEN)
    images.delete()
    return Response({'message':'Image deleted successfully.'}, status=status.HTTP_200_OK)


#---------------------------------------------Booking View--------------------------------------------------------
@extend_schema(  
    request=BookingSerializer,
    responses=BookingSerializer
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def create_booking_view(request):
    serializer= BookingSerializer(data=request.data)
    if serializer.is_valid():
        car= Car.objects.select_for_update().get(id= serializer.validated_data['car'].id) # select_for_update()=  locks the row until the transaction is completed 
        pickup_date= serializer.validated_data['pickup_date']
        return_date= serializer.validated_data['return_date']

        if not car.is_available:
            return Response({'error':'Car is unavailable.'}, status=status.HTTP_400_BAD_REQUEST)
        if car.owner == request.user:
            return Response({'error':"Can't book your own car."}, status=status.HTTP_400_BAD_REQUEST)
        if not car.available_for_rent:
            return Response({'error':"Car is not available for rent."}, status=status.HTTP_400_BAD_REQUEST)
        
        total_days= (return_date -  pickup_date).days + 1 # charging starts from pickup date
        total_price= (total_days * car.renting_price)
        booking= serializer.save(user=request.user, price=total_price, status='PENDING')
        # above, we are not doing directly serializer.save() bcz there are too many datas transferring and the serializer data may not update before our response serializer.data, to prevent o/p errors, we use a booking variable to make sure new data is saved in it and then show this new saved variable data. 
        expire_booking.apply_async(args=[str(booking.id)], countdown=1200)
        # This is for celery tasks.py, to cancel booking if payment is not made under 20 min
        return Response({'message':'Booking successfull.', 'data':BookingSerializer(booking).data}, status=status.HTTP_201_CREATED)
    return Response({'error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    responses=BookingSerializer(many=True)
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def booking_history_view(request):
    bookings= Booking.objects.filter(user=request.user)

    status_search= request.GET.get('status')
    if status_search:
        bookings= bookings.filter(status__icontains=status_search)
    
    ordering= request.GET.get('ordering')
    allowed_ordering = ['price', '-price', 'pickup_date', '-pickup_date', 'created_at', '-created_at']
    if ordering in allowed_ordering:
        bookings= bookings.order_by(ordering)
    else:
        bookings= bookings.order_by('-created_at')

    page= request.GET.get('page', 1) # if /api/cars/?page=1, here 1 will be by default
    paginator= Paginator(bookings, 5) # 5 means it will show 5 datas per page
    bookings= paginator.get_page(page) # bookings= 5 datas per page 

    serializer= BookingSerializer(bookings, many=True)
    return Response({'data':serializer.data, 'count':paginator.count, 'total_pages':paginator.num_pages, 'current_page':bookings.number}, status=status.HTTP_200_OK)


@extend_schema(
    responses=None
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def cancel_booking_view(request, booking_id):
    try:
        booking= Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return Response({'error':'Booking not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    if booking.user != request.user:
        return Response({'error':'Unauthorized request.'}, status=status.HTTP_403_FORBIDDEN)
    if booking.status=='CANCELLED': # if the booking was already cancelled
        return Response({'error':'Booking already cancelled.'}, status=status.HTTP_400_BAD_REQUEST)
    booking.status='CANCELLED'
    booking.save()
    return Response({'message':'Booking cancelled successfully.'}, status=status.HTTP_200_OK)


#-----------------------------------------------Purchase View-----------------------------------------------------
@extend_schema(
    request=PurchaseSerializer,
    responses=PurchaseSerializer
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def create_purchase_view(request):
    serializer= PurchaseSerializer(data=request.data)
    if serializer.is_valid():
        car= Car.objects.select_for_update().get(id= serializer.validated_data['car'].id) # select_for_update()= locks the row down until transaction completes.

        if not car.available_for_sale:
            return Response({'error':'Car is not available for sale.'}, status=status.HTTP_400_BAD_REQUEST)
        if not car.is_available:
            return Response({'error':'Car already sold.'}, status=status.HTTP_400_BAD_REQUEST)
        if car.owner == request.user:
            return Response({'error':"You can't buy your own car."}, status=status.HTTP_400_BAD_REQUEST)
        purchase= serializer.save(buyer=request.user, price=car.selling_price, status='PENDING')
        # above, we are not doing directly serializer.save() bcz there are too many datas transferring and the serializer data may not update before our response serializer.data, to prevent any error, we use a purchase variable to make sure new data is saved in it and then show this new saved variable data. 
        car.is_available= False
        car.available_for_sale= False
        car.save() # to save curr avaiablity data
        expire_purchase.apply_async(args=[str(purchase.id)], countdown=1200)
        # this is done for celery to cancel purchase in 20 min if payment is not made
        return Response({'message':'Purchase successful.', 'data':PurchaseSerializer(purchase).data}, status=status.HTTP_201_CREATED)
    return Response({'error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=PurchaseSerializer,
    responses=PurchaseSerializer(many=True)
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def purchase_history_view(request):
    purchase= Purchase.objects.fitler(buyer=request.user)
    search= request.GET.get('search')
    if search:
        purchase= purchase.filter(Q(car__brand__icontains=search) | Q(car__car_model__icontains=search) | Q(status__icontains=search))
    
    ordering= request.GET.get('ordering')
    ordering_allowed= ['price', '-price', 'purchased_at', '-purchased_at']
    if ordering in ordering_allowed:
        purchase= purchase.order_by(ordering)
    else:
        purchase= purchase.order_by('-purchased_at')

    page= request.GET.get('page', 1)
    paginator= Paginator(purchase, 5)
    purchase= paginator.get_page(page)
    serializer= PurchaseSerializer(purchase, many=True)
    return Response({'data':serializer.data, 'count':paginator.count, 'total_pages':paginator.num_pages, 'current_page':purchase.number}, status=status.HTTP_200_OK)


@extend_schema(
    responses=None
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def cancel_purchase_view(request, purchase_id):
    try:
        purchase= Purchase.objects.get(id=purchase_id)
    except Purchase.DoesNotExist:
        return Response({'error':"Purchase record doesn't exist."}, status=status.HTTP_404_NOT_FOUND)
    
    if purchase.buyer != request.user and purchase.car.owner != request.user: # if user is not buyer or seller
        return Response({'error':'Unauthorized request.'}, status=status.HTTP_403_FORBIDDEN)
    if purchase.status == 'CANCELLED':
        return Response({'error':'Purchase already cancelled.'}, status=status.HTTP_400_BAD_REQUEST)
    purchase.status= 'CANCELLED' # if buyer is the curr. user & the purchase was in process
    purchase.save()

    purchase.car.is_available= True # make car available back for sale or rent
    purchase.car.available_for_sale= True
    purchase.car.save() # make this new data avaibale for car model
    return Response({'message':'Purchase cancelled successfully.'}, status=status.HTTP_200_OK) 


#---------------------------------------------Payment View------------------------------------------------------
@extend_schema(
    request=PaymentSerializer,
    responses=PaymentSerializer
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def create_payment_view(request):
    serializer= PaymentSerializer(data=request.data)
    if serializer.is_valid():
        booking= serializer.validated_data.get('booking')
        purchase= serializer.validated_data.get('purchase')
        # here we use validated_data.get() bcz .get will approve if one of the operations, purchase or booking is made by user. But if we use vaidated_data[] both purchase and booking should be True or else will throw error. Since here usr can only make one of the request, we will use .get(), so that even when usr make only booking request, it still shows response.
        if booking:
            if booking.user != request.user:
                return Response({'error':'Unauthorized payment request.'}, status=status.HTTP_403_FORBIDDEN)
            else:
                amount= booking.price
        elif purchase:
            if purchase.buyer != request.user:
                return Response({'error':'Unauthorized payment request.'}, status=status.HTTP_403_FORBIDDEN)
            else:
                amount= purchase.price

        transaction_id= str(uuid.uuid4()) # creating id automatically, not allowing usr to create one themselves
        payment= serializer.save(user=request.user, amount=amount, transaction_id=transaction_id, payment_status='CONFIRMED')

        if booking:
            booking.status= 'CONFIRMED'
            booking.save()
        if purchase:
            purchase.status= 'CONFIRMED'
            purchase.car.is_available= False # no need to do this for booking, as cars will get available later
            purchase.car.available_for_sale= False
            purchase.save()

        return Response({'message':'Payment made successfully.', 'data':PaymentSerializer(payment).data}, status=status.HTTP_201_CREATED)
    return Response({'error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=PaymentSerializer,
    responses=PaymentSerializer(many=True)
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_history_view(request):
    payments= Payment.objects.filter(user=request.user)
    search= request.GET.get('search')
    if search:
        payments= payments.filter(Q(payment_method__icontains=search) | Q(payment_status__icontains=search))
    
    ordering= request.GET.get('ordering')
    ordering_allowed= ['amount', '-amount', 'paid_at', '-paid_at']
    if ordering in ordering_allowed:
        payments= payments.order_by(ordering)
    else:
        payments= payments.order_by('-paid_at')

    page= request.GET.get('page', 1)
    paginator= Paginator(payments, 5)
    payments= paginator.get_page(page)
    serializer= PaymentSerializer(payments, many=True) # keep this line here do make sure changes are made successfully.
    return Response({'data':serializer.data, 'count':paginator.count, 'total_pages':paginator.num_pages, 'current_page':payments.number}, status=status.HTTP_200_OK)


@extend_schema(
    responses=None
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def cancel_payment_view(request, payment_id):
    try:
        payment= Payment.objects.get(id=payment_id)
    except Payment.DoesNotExist:
        return Response({'error':'Payment not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    if payment.user != request.user:
        return Response({'error':'Unauthorized request.'}, status=status.HTTP_403_FORBIDDEN)
    if payment.payment_status == 'CANCELLED':
        return Response({'error':'Payment already cancelled.'}, status=status.HTTP_400_BAD_REQUEST)
    if payment.payment_status == 'CONFIRMED':
        return Response({'error': 'Payments after confirmation cannot be cancelled.'}, status=status.HTTP_400_BAD_REQUEST)
    payment.payment_status= 'CANCELLED'
    payment.save()

    if payment.booking:
        payment.booking.status= 'CANCELLED'
        payment.booking.save()
    if payment.purchase:
        payment.purchase.status= 'CANCELLED'
        payment.purchase.save()
        payment.purchase.car.is_available= True
        payment.purchase.car.available_for_sale= True
        payment.purchase.car.save()
    return Response({'message':'Payment cancelled successfully.'}, status=status.HTTP_200_OK)


#------------------------------------------Seller/Staff/Admin Dashboards------------------------------------------
@extend_schema(
    responses=dict
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def seller_dashboard_view(request):
    if request.user.role != 'SELLER':
        return Response({'error':'Only seller can access this dashboard.'}, status=status.HTTP_403_FORBIDDEN)
    
    seller_cars= Car.objects.filter(owner=request.user)
    total_cars= seller_cars.count()
    available_cars= seller_cars.filter(is_available=True).count()
    sold_cars= seller_cars.filter(available_for_sale=False, is_available=False).count()
    total_bookings= Booking.objects.filter(car__owner=request.user).count()
    confirmed_bookings= Booking.objects.filter(car__owner=request.user, status='CONFIRMED').count()
    cancelled_bookings= Booking.objects.filter(car__owner=request.user, status='CANCELLED').count()
    total_purchases= Purchase.objects.filter(car__owner=request.user, status='CONFIRMED').count()
    
    total_revenue= Payment.objects.filter(Q(booking__car__owner=request.user) | Q(purchase__car__owner=request.user), payment_status='CONFIRMED').aggregate(total=Sum('amount'))['total'] or 0
    # .aggregate= to perform SUM(), MEAN(), MAX(), or COUNT() in a single line using their functions. 
    # (total=Sum('amount'))= here, 'total' is variable for storing SUM() of amount(from payment.models) 
    # ['total'] or 0= means if revenue is made, result will be 'total', if no revenue, it shows 0 (instead of error)
    recent_payments= Payment.objects.filter(Q(booking__car__owner=request.user) | Q(purchase__car__owner=request.user), payment_status='CONFIRMED').order_by('-paid_at')[0:5]
    recent_payment_serializer= PaymentSerializer(recent_payments, many=True)
    
    return Response({'Total cars':total_cars, 'Available cars':available_cars, 'Sold cars':sold_cars, 'Total bookings':total_bookings, 'Confirmed bookings':confirmed_bookings, 'Cancelled bookings':cancelled_bookings, 'Total purchases':total_purchases, 'Total revenue':total_revenue, 'Recent payments':recent_payment_serializer.data}, status=status.HTTP_200_OK)


@extend_schema(
    responses=dict
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def staff_dashboard_view(request):
    if request.user.role != 'STAFF':
        return Response({'error':'Only staffs are allowed to access this dashboard.'}, status=status.HTTP_403_FORBIDDEN)
    
    pending_bookings= Booking.objects.filter(status='PENDING').count()
    pending_purchases= Purchase.objects.filter(status='PENDING').count()
    pending_payments= Payment.objects.filter(payment_status='PENDING').count()
    total_users= User.objects.count()
    total_sellers= User.objects.filter(role='SELLER').count()
    return Response({'Pending bookings':pending_bookings, 'Pending purchases':pending_purchases, 'Pending payments':pending_payments, 'Total users':total_users, 'Total sellers':total_sellers}, status=status.HTTP_200_OK)


@extend_schema(
    responses=dict
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard_view(request):
    if request.user.role != 'ADMIN':
        return Response({'error':'Only admins can access this dashboard.'}, status=status.HTTP_403_FORBIDDEN)
    
    total_user= User.objects.count()
    total_sellers= User.objects.filter(role='SELLER').count()
    total_staffs= User.objects.filter(role='STAFF').count()
    total_cars= Car.objects.count()
    total_bookings= Booking.objects.count()
    total_purchases= Purchase.objects.count()
    total_payments= Payment.objects.count()
    total_revenue= Payment.objects.filter(payment_status='CONFIRMED').aggregate(revenue=Sum('amount'))['revenue'] or 0
    return Response({'Total number of users':total_user, 'Number of sellers':total_sellers, 'Number of staff members':total_staffs, 'Number of cars listed':total_cars, 'Total bookings':total_bookings, 'Number of purchases':total_purchases, 'Total payment':total_payments, 'Total revenue':total_revenue}, status=status.HTTP_200_OK)


#---------------------------------------Seller/Customer View-------------------------------------------------------
@extend_schema(
    request=ConversationSerializer,
    responses=ConversationSerializer
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_conversation_view(request, car_id):
    try:
        car= Car.objects.get(id=car_id)
    except Car.DoesNotExist:
        return Response({'error':'Car not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    if car.owner == request.user:
        return Response({'error':'cannot chat with yourself.'}, status=status.HTTP_400_BAD_REQUEST)
    conversation, created= Conversation.objects.get_or_create(buyer=request.user, seller=car.owner, car=car)
    serializer= ConversationSerializer(conversation)
    return Response({'message':'Conversation created' if created else 'Conversation found.', 'data':serializer.data}, status=status.HTTP_200_OK if conversation else status.HTTP_201_CREATED)


@extend_schema(
    request=MessageSerializer,
    responses=MessageSerializer(many=True)
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def conversation_message_view(request, conversation_id):
    try: 
        conversation= Conversation.objects.get(id=conversation_id)
    except Conversation.DoesNotExist:
        return Response({'error':'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.user not in [conversation.buyer, conversation.seller]:
        return Response({'error':'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    Message.objects.filter(conversation=conversation, is_read=False).exclude(sender=request.user).update(is_read=True) # to mark text as read as soon as someone else and not sender opens chat.
    messages= conversation.messages.all().order_by('-created_at')

    search= request.GET.get('search')
    if search:
        messages= messages.filter(text__icontains=search)

    page= request.GET.get('page', 1)
    paginator= Paginator(messages, 5)
    messages= paginator.get_page(page)
    serializer= MessageSerializer(messages, many=True)
    return Response({'data':serializer.data, 'count':paginator.count, 'current_page':messages.number, 'total_pages':paginator.num_pages}, status=status.HTTP_200_OK)


@extend_schema(
    request=MessageSerializer,
    responses=MessageSerializer
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message_view(request, conversation_id):
    try:
        conversation= Conversation.objects.get(id=conversation_id)
    except Conversation.DoesNotExist:
        return Response({'error':'Conversation not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.user not in [conversation.buyer, conversation.seller]:
        return Response({'error':'Unautorized request.'}, status=status.HTTP_403_FORBIDDEN)

    serializer= MessageSerializer(data=request.data)
    if serializer.is_valid():
        message= serializer.save(sender=request.user, conversation=conversation)
        return Response({'data':MessageSerializer(message).data}, status=status.HTTP_201_CREATED)
    return Response({'error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)