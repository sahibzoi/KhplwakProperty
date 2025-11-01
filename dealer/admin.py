# dealer/admin.py
from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import GroupAdmin, UserAdmin

from .models import (
    Investor,
    PropertyItem,
    Transaction,
    Commission,
    Expense,
    Income,
)


# ---------- Common: restrict a model to superusers only ----------
class SuperuserOnlyMixin:
    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


# ---------- PropertyItem ----------
@admin.register(PropertyItem)
class PropertyItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "address",
        "city",
        "listing_type",
        "status",
        "sale_price",
        "rent_monthly",
    )
    list_filter = ("city", "listing_type", "status")
    search_fields = ("address", "city", "area_name", "owner_name")
    ordering = ("-id",)
    list_per_page = 20


# ---------- Transaction ----------
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "property_item", "investor", "transaction_type", "amount")
    list_filter = ("transaction_type",)
    search_fields = ("property_item__address", "investor__full_name")
    ordering = ("-id",)
    list_per_page = 20


# ---------- Investor ----------
@admin.register(Investor)
class InvestorAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "phone",
        "investor_type",
        "status",
        "invested_amount",
        "created_at",
    )
    list_filter = ("investor_type", "status")
    search_fields = ("full_name", "surname", "phone", "location")
    ordering = ("-id",)
    list_per_page = 20


# ---------- Commission ----------
@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "property_item",
        "deal_type",
        "commission_type",
        "commission_value",
        "deal_amount",
        "total_earned",
        "created_at",
    )
    list_filter = ("deal_type", "commission_type")
    search_fields = ("property_item__address",)
    ordering = ("-id",)
    readonly_fields = ("total_earned",)
    list_per_page = 20


# ---------- Expense ----------
@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "category", "property_item", "amount", "created_by")
    list_filter = ("category", "date")
    search_fields = ("description", "property_item__address")
    ordering = ("-date", "-id")
    list_per_page = 20


# ---------- Income ----------
@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "source", "property_item", "amount", "created_by")
    list_filter = ("source", "date")
    search_fields = ("description", "property_item__address")
    ordering = ("-date", "-id")
    list_per_page = 20


# ---------- Auth models: superuser-only ----------
# Replace default registrations so only superusers can see/manage them
try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass

@admin.register(Group)
class SuperuserOnlyGroupAdmin(SuperuserOnlyMixin, GroupAdmin):
    pass


try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

@admin.register(User)
class SuperuserOnlyUserAdmin(SuperuserOnlyMixin, UserAdmin):
    pass


# ---------- Admin Site Branding ----------
admin.site.site_header = "Khplwak Property — Admin"
admin.site.site_title = "Khplwak Admin"
admin.site.index_title = "Dealer Back-Office Dashboard"
