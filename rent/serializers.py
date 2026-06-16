from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Car, CarImage, Booking, Purchase, Payment, Conversation, Message
from datetime import date

class RegistrationSerializer(serializers.ModelSerializer):
    password= serializers.CharField(write_only=True, min_length=3)
    password2= serializers.CharField(write_only=True, min_length=3)
    role= serializers.ChoiceField(choices=[('CUSTOMER', 'Customer'), ('SELLER', 'Seller')], default='CUSTOMER')
    class Meta:
        model= User
        fields= ['id', 'username', 'photo', 'email', 'password', 'password2', 'phone_no', 'role', 'is_online']
        extra_kwargs= {'id':{'read_only':True}}

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError({'email':'Email already exixsts.'})
        return value
    
    def validate_role(self, value):
        allowed_roles= ['CUSTOMER', 'SELLER']
        if value not in allowed_roles:
            raise serializers.ValidationError({'error':'You can only register as customer or seller only.'})
        return value
        
    def validate_username(self, value):
        if len(value) < 4: # value=username
            raise serializers.ValidationError({'username':'Username is too short. Should be atleast of four letters'}) 
        return value
    
    def validate_phone_no(self, value):
        if not value.isdigit():
            raise serializers.ValidationError({'phone_no':'Phone number should contain only digits.'})
        if len(value) < 10 or len(value) > 12:
            raise serializers.ValidationError({'phone_no':'Phone number should be of 10 or 12 digits atleast.'})
        return value 
    
    def validate(self, attrs): # this validate is a keyword, so don't change
        password= attrs.get('password')
        password2= attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError({'password':'Both passwords do not match'})
        return attrs
    
    def create(self, validated_data): # this create is a keyword, so don't change
        validated_data.pop('password2') # this should not be saved for new user, so we remove it
        role= validated_data.get('role', 'CUSTOMER')
        if role not in ['CUSTOMER', 'SELLER']:
            role = 'CUSTOMER' # even if usr manually types ADMIN it still take CONSUMER
        user= User.objects.create(email=validated_data['email'], username=validated_data['username'], phone_no=validated_data['phone_no'], role=role)
        user.set_password(validated_data['password'])
        user.save()
        print(validated_data)
        return user
    

class LoginSerializer(serializers.Serializer):
    email= serializers.EmailField()
    password= serializers.CharField(write_only=True)

    def validate(self, attrs):
        email= attrs.get('email')
        password= attrs.get('password')
        user= authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError({'error':'Invalid Email or password.'})
        attrs['user']= user
        return attrs
    

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model= User
        fields= ['id', 'username', 'photo', 'email', 'phone_no', 'role']
        read_only_fields = ['id', 'email', 'role']
        
    def validate_username(self, value):
            if len(value) < 4:
                raise serializers.ValidationError({'username':'Username is too short. Should be of atleast 4 letters.'})
            return value
        
    def validate_phone_no(self, value):
            if not value.isdigit():
                raise serializers.ValidationError({'phone_no':'Phone number can onluy be integers.'})
            if len(value) < 10 or len(value) > 12:
                raise serializers.ValidationError({'phone_no':'Phone number should be between 10 and 12 digits.'})
            return value   


class ChangePasswordSerializer(serializers.Serializer):
    old_password= serializers.CharField(write_only=True, min_length=4)
    new_password= serializers.CharField(write_only=True, min_length=4)
    confirm_password= serializers.CharField(write_only=True, min_length=4)

    def validate(self, attrs):
        old_password= attrs.get('old_password')
        new_password= attrs.get('new_password')
        confirm_password= attrs.get('confirm_password')
        user= self.context.get('user') # this context was sent from views.py

        if not user.check_password(old_password):
            raise serializers.ValidationError({'error':'Previous password is incorrect.'}) 
        elif new_password != confirm_password:
            raise serializers.ValidationError({'error':'Both passwords do not match.'})
        elif new_password == old_password:
            raise serializers.ValidationError({'error':'Old and new passwords cannot be same.'})
        return attrs
    

class ForgotPasswordSerializer(serializers.Serializer):
    email= serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError({'error':'There is no account with this email.'})
        return value
    

class ResetPasswordSerializer(serializers.Serializer):
    new_password= serializers.CharField(write_only=True, min_length=4)
    confirm_password= serializers.CharField(write_only=True, min_length=4)
    
    def validate(self, attrs):
        new_password= attrs.get('new_password')
        confirm_password= attrs.get('confirm_password')

        if new_password != confirm_password:
            raise serializers.ValidationError({'error':'Both passwords do not match.'})
        return attrs
    

class CarSerializer(serializers.ModelSerializer):
    owner= serializers.StringRelatedField(source='owner.username', read_only=True)
    
    class Meta:
        model= Car
        fields= '__all__'
        read_only_fields= ['id', 'owner', 'created_at']

    def validate_renting_price(self, value):
        if value <= 0:
            raise serializers.ValidationError({'error':'Renting price must be a positive number.'})
        return value
    
    def validate_selling_price(self, value):
        if value <= 0:
            raise serializers.ValidationError({'error':'Selling price must be a positive number.'})
        return value
    

class CarImageSerializer(serializers.ModelSerializer):
    class Meta:
        model= CarImage
        fields= '__all__'
        read_only_fields= ['id', 'uploaded_at']
    

class BookingSerializer(serializers.ModelSerializer):
    user= serializers.StringRelatedField(read_only=True) # here string field bcz in models, they are foreign keys
    price= serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model= Booking
        fields= '__all__'
        read_only_fields= ['id', 'user', 'price', 'created_at', 'status']

    def validate(self, attrs):
        pickup_date= attrs.get('pickup_date')
        return_date= attrs.get('return_date')
        car= attrs.get('car')
        
        if pickup_date < date.today():
            raise serializers.ValidationError({'error':'Choose a valid pickup date.'})
        if pickup_date >= return_date:
            raise serializers.ValidationError({'error':'Choose a valid return date.'})
        
        overlapping_booking= Booking.objects.filter(car=car, status__in=['CONFIRMED', 'PENDING'], pickup_date__lt=return_date, return_date__gt=pickup_date).exists() # if another usr has already made the request for car before this usr
        if overlapping_booking:
            raise serializers.ValidationError({'issue':'Car is already booked for selected data.'})
        return attrs


class PurchaseSerializer(serializers.ModelSerializer):
    buyer= serializers.CharField(source='buyer.username', read_only=True) 
    price= serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model= Purchase
        fields= '__all__'
        read_only_fields= ['id', 'buyer', 'status', 'purchased_at', 'price']
    

class PaymentSerializer(serializers.ModelSerializer):
    user= serializers.StringRelatedField(read_only=True) # here string field bcz in models, they are foreign keys

    class Meta:
        model= Payment
        fields= '__all__'
        read_only_fields= ['id', 'amount', 'user', 'payment_status', 'paid_at', 'transaction_id']

    def validate(self, attrs):
        booking= attrs.get('booking')
        purchase= attrs.get('purchase')
        if booking and purchase:
            raise serializers.ValidationError({'error':'One payment cannot be for both booking and purchasing.'})
        if not booking and not purchase:
            raise serializers.ValidationError({'error':'Payment has to be for atleast one, booking or purchasing.'})
        return attrs
    

class ConversationSerializer(serializers.ModelSerializer):
    seller= serializers.CharField(source='seller.username', read_only=True)
    buyer= serializers.CharField(source='buyer.username', read_only=True)

    class Meta:
        model= Conversation
        fields= '__all__'
        read_only_fields= ['created_at']


class MessageSerializer(serializers.ModelSerializer):
    sender= serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model= Message
        fields= '__all__'
        read_only_fields= ['id', 'is_read', 'sender', 'created_at', 'conversation']

    def validate(self, attrs):
        text= attrs.get('text')
        image= attrs.get('image')
        file= attrs.get('file')
        if not text and not image and not file:
            raise serializers.ValidationError({'error':'Message must contain text, file or image.'})
        return attrs


