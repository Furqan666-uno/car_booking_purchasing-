from django.contrib import admin
from django.utils.html import format_html
from .models import User, Car, CarImage, Booking, Purchase, Payment, Message, Conversation


class UserAdmin(admin.ModelAdmin):
    # TO DISPLAY OF THE FRONT PAGE
    list_display = ['id', 'email', 'username', 'role', 'phone_no', 'is_active', 'photo']

    def photo_preview(self, obj): # THIS WILL DISPLAY IMAGE ON ADMIN PAGE
        if obj.photo:
            return format_html('<img src="{}" width="80" height="60" />',obj.photo.url)
        return "No Image"
    photo_preview.short_description= "Preview"

    list_filter = ['role', 'is_active'] # SIDEBAR FILTERS
    search_fields = ['email', 'username', 'phone_no'] # SEARCH BAR
    ordering = ['email'] # DEFAULT SORTING
    list_display_links = ['email', 'username'] # CLICKABLE LINKS
    list_per_page = 10 # PAGINATION
    readonly_fields = ['id', 'last_login', 'date_joined'] # READ ONLY FIELDS

    # DETAIL PAGE CATEGORIES
    fieldsets = (
        ('Personal Information', {'fields':('id', 'username', 'email', 'phone_no', 'photo')}),
        ('Role & Permissions', {'fields':('role', 'is_staff', 'is_superuser', 'is_active')}),
        ('Important Dates', {'fields':('last_login', 'date_joined')}),
        )
    
    # CREATE NEW USER PAGE
    add_fieldsets = [
        (None, {"classes": ["wide"], "fields": ["email", "username", "phone_no", "password1", "password2"]})
        ]
admin.site.register(User, UserAdmin)


class CarAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner', 'car_model', 'brand', 'release_year', 'fuel_type', 'transmission_type', 'seats', 'listing_type', 'renting_price', 'selling_price', 'available_for_rent', 'available_for_sale', 'created_at', 'is_available']
    list_filter = ['transmission_type', 'fuel_type', 'is_available'] # SIDEBAR FILTERS
    search_fields = ['owner__username', 'owner__email', 'car_model', 'brand'] # SEARCH BAR
    ordering = ['-created_at'] # DEFAULT SORTING
    list_display_links = ['car_model', 'id'] # CLICKABLE LINKS
    list_per_page = 10 # PAGINATION
    readonly_fields = ['id', 'created_at'] # READ ONLY FIELDS
    list_editable = ['available_for_rent', 'available_for_sale', 'is_available'] # ADMIN CAN EDIT FIELDS

    # DETAIL PAGE CATEGORIES
    fieldsets = (
        ('Car Information', {'fields':(
                ('car_model', 'brand', 'seats'), 
                ('fuel_type', 'transmission_type'), 
                ('release_year'),
                )
            }), # fields are in seperate () to arrange them in horizontal layout
        ('Pricing Information', {'fields':('listing_type', 'renting_price', 'selling_price')}),
        ('Other Info', {'fields':('owner', 'available_for_rent', 'available_for_sale', 'created_at', 'is_available')}),
        )
    
    # CREATE NEW CAR PAGE
    add_fieldsets = [
        (None, {"classes": ["wide"], "fields": ['owner', 'car_model', 'brand', 'release_year', 'fuel_type', 'transmission_type', 'seats']})
        ]
admin.site.register(Car, CarAdmin)


class CarImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'car', 'image', 'uploaded_at']

    def image_preview(self, obj): # THIS WILL DISPLAY IMAGE ON ADMIN PAGE
        if obj.image:
            return format_html('<img src="{}" width="80" height="60" />',obj.image.url)
        return "No Image"
    image_preview.short_description= "Preview"

    list_filter = ['car'] # SIDEBAR FILTERS
    search_fields = ['car__car_model', 'car__brand'] # SEARCH BAR
    ordering = ['-uploaded_at'] # DEFAULT SORTING
    list_display_links = ['car', 'id'] # CLICKABLE LINKS
    list_per_page = 10 # PAGINATION
    readonly_fields = ['id', 'uploaded_at'] # READ ONLY FIELDS
    # list_editable = ['image'] # ADMIN CAN EDIT FIELDS

    # DETAIL PAGE CATEGORIES
    fieldsets = (
        ('Car Image Information', {'fields':('id', 'car', 'image', 'uploaded_at')}),
        )
admin.site.register(CarImage, CarImageAdmin)


class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'car', 'pickup_date', 'return_date', 'price', 'status', 'created_at']
    list_filter = ['status', 'created_at'] # SIDEBAR FILTERS
    search_fields = ['user__username', 'car__car_model', 'car__brand'] # SEARCH BAR
    ordering = ['-price'] # DEFAULT SORTING
    list_display_links = ['id', 'user'] # CLICKABLE LINKS
    list_per_page = 10 # PAGINATION
    readonly_fields = ['id', 'created_at'] # READ ONLY FIELDS

    # DETAIL PAGE CATEGORIES
    fieldsets = (
        ('Booking Information', {'fields':('id', 'user', 'car', 'price', 'created_at')}),
        ('Current Status', {'fields':('status',)}),
        ('Important Dates', {'fields':('pickup_date', 'return_date')}),
        )
admin.site.register(Booking, BookingAdmin)


class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['id', 'buyer', 'car', 'price', 'status', 'purchased_at']
    list_filter = ['status', 'purchased_at'] # SIDEBAR FILTERS
    search_fields = ['buyer__username', 'car__car_model', 'car__brand'] # SEARCH BAR
    ordering = ['-price'] # DEFAULT SORTING
    list_display_links = ['id', 'buyer', 'car'] # CLICKABLE LINKS
    list_per_page = 10 # PAGINATION
    readonly_fields = ['id', 'purchased_at'] # READ ONLY FIELDS

    # DETAIL PAGE CATEGORIES
    fieldsets = (
        ('Purchase Information', {'fields':('id', 'price', 'status', 'purchased_at', 'car')}),
        ('Buyer Information', {'fields':('buyer',)}),
        )
admin.site.register(Purchase, PurchaseAdmin)


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'booking', 'purchase', 'amount', 'payment_method', 'payment_status', 'paid_at', 'transaction_id']
    list_filter = ['payment_status', 'payment_method'] # SIDEBAR FILTERS
    search_fields = ['user__username'] # SEARCH BAR
    ordering = ['-amount'] # DEFAULT SORTING
    list_display_links = ['user', 'id', 'transaction_id'] # CLICKABLE LINKS
    list_per_page = 10 # PAGINATION
    readonly_fields = ['id', 'paid_at', 'transaction_id'] # READ ONLY FIELDS
    list_editable = ['payment_status'] # ADMIN CAN EDIT FIELDS

    # DETAIL PAGE CATEGORIES
    fieldsets = (
        ('Payment Details', {'fields':('transaction_id', 'paid_at', 'payment_status', 'payment_method', 'amount')}),
        ('User Information', {'fields':('id', 'user', 'booking', 'purchase')}),
        )
admin.site.register(Payment, PaymentAdmin)


class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'buyer', 'seller', 'car', 'created_at']
    # list_filter = ['payment_status', 'payment_method'] # SIDEBAR FILTERS
    search_fields = ['buyer__username', 'seller__username', 'buyer__email', 'seller__email',] # SEARCH BAR
    ordering = ['-created_at'] # DEFAULT SORTING
    list_display_links = ['buyer', 'id', 'seller'] # CLICKABLE LINKS
    list_per_page = 10 # PAGINATION
    readonly_fields = ['id', 'created_at'] # READ ONLY FIELDS
    # list_editable = ['payment_status'] # ADMIN CAN EDIT FIELDS

    # DETAIL PAGE CATEGORIES
    fieldsets = (
        ('Conversation Details', {'fields':('id', 'buyer', 'seller', 'car', 'created_at')}),
        )
admin.site.register(Conversation, ConversationAdmin)


class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'sender', 'text', 'file', 'image', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at'] # SIDEBAR FILTERS
    search_fields = ['sender__username', 'sender__email'] # SEARCH BAR
    ordering = ['-created_at'] # DEFAULT SORTING
    list_display_links = ['conversation', 'id', 'sender'] # CLICKABLE LINKS
    list_per_page = 10 # PAGINATION
    readonly_fields = ['id', 'created_at', 'text', 'sender'] # READ ONLY FIELDS
    # list_editable = ['payment_status'] # ADMIN CAN EDIT FIELDS

    def sender_name(self, obj): # so that we can get sender's username & email shown directly in admin pages
        return obj.sender.username
    sender_name.short_description = "Username"
    def sender_email(self, obj):
        return obj.sender.email
    sender_email.short_description = "Email"
    
    # DETAIL PAGE CATEGORIES
    fieldsets = (
        ('Message Details', {'fields':('id', 'conversation', 'is_read', 'created_at', 'text', 'file', 'image')}),
        ('Sender Details', {'fields':('sender_username','sender_email')}),
        )
admin.site.register(Message, MessageAdmin)