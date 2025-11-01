from django import forms
from .models import Investor, PropertyItem, Transaction, Commission
import re
from django import forms
from .models import Expense, Income





AF_PHONE_REGEX = re.compile(
    r"""^(
        (\+93|0093)\s?\d{2,3}[-\s]?\d{3}[-\s]?\d{3}$   # +93 / 0093 formats
        |
        0?\d{9}$                                      # 0700123456 or 700123456
    )""",
    re.VERBOSE
)

class InvestorForm(forms.ModelForm):
    class Meta:
        model = Investor
        fields = [
            'full_name',
            'surname',
            'location',
            'phone',
            'whatsapp',
            'invested_amount',
            'investor_type',
            'status',
            'id_document',
            'notes',
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()

        # Allow blank (optional field). If you want phone required, remove this block.
        if phone == '':
            return phone

        # normalize (remove spaces and dashes just for validation check)
        compact = phone.replace(' ', '').replace('-', '')

        if not AF_PHONE_REGEX.match(compact):
            raise forms.ValidationError(
                "Enter a valid Afghanistan number like +93XXXXXXXXX, 0093XXXXXXXXX, or 07XXXXXXXX."
            )

        return phone

    def clean_whatsapp(self):
        wa = self.cleaned_data.get('whatsapp', '').strip()

        if wa == '':
            return wa

        compact = wa.replace(' ', '').replace('-', '')

        if not AF_PHONE_REGEX.match(compact):
            raise forms.ValidationError(
                "Enter a valid WhatsApp number (Afghanistan format)."
            )

        return wa
class PropertyItemForm(forms.ModelForm):
    class Meta:
        model = PropertyItem
        fields = [
            # Basic info
            "address",
            "city",
            "area_name",
            "property_type",
            "listing_type",
            "status",
            "size",
            "floor_area_sqft",

            # Physical / structure details
            "bedrooms",
            "bathrooms",
            "kitchens",
            "floor_no",
            "total_floors",
            "parking_spaces",

            # Deal info
            "sale_price",
            "rent_monthly",
            "rent_deposit",
            "mortgage_amount",
            "mortgage_terms",

            # Owner / internal
            "owner_name",
            "owner_contact",
            "description",
        ]

        widgets = {
            # BASIC INFO
            "address": forms.TextInput(attrs={
                "placeholder": "Full address",
                "class": "form-control"
            }),
            "city": forms.TextInput(attrs={
                "placeholder": "City name",
                "class": "form-control"
            }),
            "area_name": forms.TextInput(attrs={
                "placeholder": "Area / Block / Street",
                "class": "form-control"
            }),
            "property_type": forms.TextInput(attrs={
                "placeholder": "House, Apartment, Shop, Land...",
                "class": "form-control"
            }),

            # These are ChoiceFields in the model, so Select makes sense
            "listing_type": forms.Select(attrs={
                "class": "form-select"
            }),
            "status": forms.Select(attrs={
                "class": "form-select"
            }),

            "size": forms.TextInput(attrs={
                "placeholder": "1 Biswa / 100 sqm",
                "class": "form-control"
            }),
            "floor_area_sqft": forms.TextInput(attrs={
                "placeholder": "e.g. 120 sqm covered",
                "class": "form-control"
            }),

            # STRUCTURE
            "bedrooms": forms.NumberInput(attrs={
                "placeholder": "3",
                "class": "form-control",
                "min": 0
            }),
            "bathrooms": forms.NumberInput(attrs={
                "placeholder": "2",
                "class": "form-control",
                "min": 0
            }),
            "kitchens": forms.NumberInput(attrs={
                "placeholder": "1",
                "class": "form-control",
                "min": 0
            }),
            "floor_no": forms.TextInput(attrs={
                "placeholder": "Ground / 1st / 2nd",
                "class": "form-control"
            }),
            "total_floors": forms.NumberInput(attrs={
                "placeholder": "Total floors in building",
                "class": "form-control",
                "min": 0
            }),
            "parking_spaces": forms.NumberInput(attrs={
                "placeholder": "1 or 2",
                "class": "form-control",
                "min": 0
            }),

            # DEAL INFO
            "sale_price": forms.NumberInput(attrs={
                "placeholder": "Only if for sale",
                "class": "form-control",
                "min": 0,
                "step": "0.01",
            }),
            "rent_monthly": forms.NumberInput(attrs={
                "placeholder": "Only if for rent",
                "class": "form-control",
                "min": 0,
                "step": "0.01",
            }),
            "rent_deposit": forms.NumberInput(attrs={
                "placeholder": "Deposit / advance",
                "class": "form-control",
                "min": 0,
                "step": "0.01",
            }),
            "mortgage_amount": forms.NumberInput(attrs={
                "placeholder": "If mortgage / grawi",
                "class": "form-control",
                "min": 0,
                "step": "0.01",
            }),
            "mortgage_terms": forms.Textarea(attrs={
                "rows": 2,
                "placeholder": "Terms, return time, witnesses...",
                "class": "form-control"
            }),

            # OWNER / NOTES
            "owner_name": forms.TextInput(attrs={
                "placeholder": "Owner full name",
                "class": "form-control"
            }),
            "owner_contact": forms.TextInput(attrs={
                "placeholder": "Owner phone / WhatsApp",
                "class": "form-control"
            }),
            "description": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "Internal notes / highlights",
                "class": "form-control"
            }),
        }


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            "property_item",
            "investor",
            "transaction_type",
            "amount",
        ]
        widgets = {
            "property_item": forms.Select(attrs={
                "class": "form-select"
            }),
            "investor": forms.Select(attrs={
                "class": "form-select"
            }),
            "transaction_type": forms.Select(
                choices=[
                    ("buy", "Buy / Money Spent"),
                    ("sell", "Sell / Money Received"),
                ],
                attrs={"class": "form-select"}
            ),
            "amount": forms.NumberInput(attrs={
                "placeholder": "AFN",
                "class": "form-control",
                "min": 0,
                "step": "0.01",
            }),
        }


class CommissionForm(forms.ModelForm):
    class Meta:
        model = Commission
        fields = [
            "property_item",
            "deal_type",
            "deal_amount",
            "commission_type",
            "commission_value",
            "notes",
        ]
        widgets = {
            "property_item": forms.Select(attrs={
                "class": "form-select"
            }),
            "deal_type": forms.Select(attrs={
                "class": "form-select"
            }),
            "deal_amount": forms.NumberInput(attrs={
                "placeholder": "Full deal value (AFN)",
                "class": "form-control",
                "min": 0,
                "step": "0.01",
            }),
            "commission_type": forms.Select(attrs={
                "class": "form-select"
            }),
            "commission_value": forms.NumberInput(attrs={
                "placeholder": "Percent or fixed AFN",
                "class": "form-control",
                "min": 0,
                "step": "0.01",
            }),
            "notes": forms.Textarea(attrs={
                "rows": 2,
                "placeholder": "Optional notes (who paid, split, etc.)",
                "class": "form-control"
            }),
        }



class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = [
            'property_item',
            'description',
            'category',
            'amount',
            'date',
            'remarks',
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'remarks': forms.Textarea(attrs={'rows': 2}),
        }


class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = [
            'property_item',
            'description',
            'source',
            'amount',
            'date',
            'remarks',
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'remarks': forms.Textarea(attrs={'rows': 2}),
        }
