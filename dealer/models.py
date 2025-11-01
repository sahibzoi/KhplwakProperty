from django.db import models
from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


afghan_phone_validator = RegexValidator(
    regex=r'^(?:\+93|0)?7\d{8}$',
    message="Enter a valid Afghan phone number (e.g. +93700123456 or 0700123456)."
)

class Investor(models.Model):
    full_name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=150, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    whatsapp = models.CharField(max_length=20, blank=True, null=True)
    investor_type = models.CharField(
        max_length=20,
        choices=[
            ('partner', 'Partner / Investor'),
            ('client', 'Client / Buyer'),
            ('other', 'Other'),
        ],
        default='partner'
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('inactive', 'Inactive'),
        ],
        default='active'
    )
    id_document = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    invested_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.full_name

class PropertyItem(models.Model):
    LISTING_CHOICES = [
        ('sale', 'For Sale'),
        ('rent', 'For Rent'),
        ('mortgage', 'Mortgage / Grawi'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('sold', 'Sold'),
        ('rented', 'Rented'),
        ('mortgaged', 'Mortgaged'),
        ('pending', 'Pending / In Process'),
    ]

    # Basic info
    address        = models.CharField(max_length=200)
    city           = models.CharField(max_length=100, blank=True, null=True)
    area_name      = models.CharField(max_length=100, blank=True, null=True)
    property_type  = models.CharField(max_length=50)  # House, Shop, Land, Apartment, etc.

    listing_type   = models.CharField(
        max_length=20,
        choices=LISTING_CHOICES,
        default='sale'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available'
    )

    size           = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Size in Biswa"
    )

    # Physical / structure details
    bedrooms       = models.PositiveIntegerField(blank=True, null=True)
    bathrooms      = models.PositiveIntegerField(blank=True, null=True)
    kitchens       = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="How many kitchens?"
    )

    floor_no       = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Which floor is THIS unit on? e.g. Ground, 1st, 2nd"
    )

    total_floors   = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Total floors in the building"
    )

    parking_spaces = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="How many car parking slots?"
    )

    floor_area_sqft = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Covered area (sq ft / marla / etc.)"
    )

    # Deal info
    # --- Sale fields ---
    sale_price     = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)

    # --- Rent fields ---
    rent_monthly   = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    rent_deposit   = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)

    # --- Mortgage / Grawi fields ---
    mortgage_amount = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    mortgage_terms  = models.TextField(blank=True, null=True)

    # Internal / owner
    owner_name     = models.CharField(max_length=100, blank=True, null=True)
    owner_contact  = models.CharField(max_length=100, blank=True, null=True)
    description    = models.TextField(blank=True, null=True)

    created_at     = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address



class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('buy', 'Buy / Money Spent'),
        ('sell', 'Sell / Money Received'),
    ]

    property_item    = models.ForeignKey(PropertyItem, on_delete=models.CASCADE)
    investor         = models.ForeignKey(Investor, on_delete=models.CASCADE)

    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPE_CHOICES
    )

    amount           = models.DecimalField(max_digits=18, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.property_item.address}"



class Commission(models.Model):
    DEAL_TYPE_CHOICES = [
        ('sale', 'Sale'),
        ('rent', 'Rent'),
        ('mortgage', 'Mortgage / Grawi'),
    ]

    COMM_TYPE_CHOICES = [
        ('percent', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]

    property_item = models.ForeignKey(PropertyItem, on_delete=models.CASCADE)

    # sale / rent / mortgage
    deal_type = models.CharField(max_length=20, choices=DEAL_TYPE_CHOICES)

    # total deal value (sale price, total key money, etc.)
    deal_amount = models.DecimalField(max_digits=18, decimal_places=2)

    # how commission is decided
    commission_type = models.CharField(max_length=10, choices=COMM_TYPE_CHOICES)

    # if type=percent -> percentage number (ex: 1.5)
    # if type=fixed   -> actual AFN amount
    commission_value = models.DecimalField(max_digits=10, decimal_places=2)

    # auto-filled final amount of money you earned on this deal
    total_earned = models.DecimalField(max_digits=18, decimal_places=2, editable=False)

    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Calculate final earning before saving
        if self.commission_type == 'percent':
            self.total_earned = (self.deal_amount * self.commission_value) / 100
        else:
            self.total_earned = self.commission_value
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_deal_type_display()} | {self.property_item.address} | {self.total_earned}"


class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('purchase', 'Property Purchase / Payment to Owner'),
        ('maintenance', 'Repair / Maintenance / Work'),
        ('commission', 'Broker / Dealer Commission Paid'),
        ('legal', 'Documents / Legal / Transfer'),
        ('office', 'Office / Fuel / Travel'),
        ('other', 'Other'),
    ]

    property_item = models.ForeignKey(
        PropertyItem,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text="Related property (optional)"
    )

    description = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)

    amount = models.DecimalField(max_digits=18, decimal_places=2)

    date = models.DateField(default=timezone.now)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Expense {self.amount} AFN - {self.category}"


class Income(models.Model):
    SOURCE_CHOICES = [
        ('sale', 'Property Sale / Installment Received'),
        ('rent', 'Rental Income'),
        ('investor_return', 'Paid Back by Buyer / Investor Return'),
        ('other', 'Other'),
    ]

    property_item = models.ForeignKey(
        PropertyItem,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text="Related property (optional)"
    )

    description = models.CharField(max_length=200)
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES)

    amount = models.DecimalField(max_digits=18, decimal_places=2)

    date = models.DateField(default=timezone.now)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Income {self.amount} AFN - {self.source}"