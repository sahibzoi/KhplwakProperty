from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    # ================= DASHBOARD / HOME =================
    path('', views.home, name='home'),
    path('dashboard/', views.home, name='dashboard'),

    # ================= INVESTORS =================
    path('investors/', views.investor_list, name='investor_list'),
    path('investors/new/', views.investor_create, name='investor_create'),
    path('investors/<int:id>/', views.investor_detail, name='investor_detail'),
    path('investors/<int:id>/edit/', views.investor_edit, name='investor_edit'),
    path('investors/<int:id>/delete/', views.investor_delete, name='investor_delete'),

    # ================= PROPERTIES =================
    path('properties/', views.property_list, name='property_list'),
    path('properties/new/', views.property_create, name='property_create'),
    path('properties/<int:id>/detail/', views.property_detail, name='property_detail'),
    path('properties/<int:id>/edit/', views.property_edit, name='property_edit'),
    path('properties/<int:id>/delete/', views.property_delete, name='property_delete'),
    path('properties/export/csv/', views.export_properties_csv, name='export_properties_csv'),

    # ================= COMMISSIONS =================
    path('commissions/', views.commission_list, name='commission_list'),
    path('commissions/new/', views.commission_create, name='commission_create'),
    path('commissions/<int:id>/edit/', views.commission_edit, name='commission_edit'),
    path('commissions/<int:id>/delete/', views.commission_delete, name='commission_delete'),

    # ================= TRANSACTIONS =================
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/new/', views.transaction_create, name='transaction_create'),
    path('transactions/<int:id>/edit/', views.transaction_edit, name='transaction_edit'),
    path('transactions/<int:id>/delete/', views.transaction_delete, name='transaction_delete'),

    # ================= EXPENSES =================
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/new/', views.expense_create, name='expense_create'),
    path('expenses/<int:id>/edit/', views.expense_edit, name='expense_edit'),
    path('expenses/<int:id>/delete/', views.expense_delete, name='expense_delete'),

    # ================= INCOMES =================
    path('incomes/', views.income_list, name='income_list'),
    path('incomes/new/', views.income_create, name='income_create'),

    # ================= REPORTS =================
    path('reports/finance/', views.finance_report, name='finance_report'),

    # ================= BACKUP & TOOLS =================
    path('backup/dashboard/', views.backup_dashboard, name='backup_dashboard'),
    path('backup/export_csv/', views.export_backup_csv, name='export_backup_csv'),

    # ================= AUTH =================
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='accounts/login.html',
            redirect_authenticated_user=True
        ),
        name='login'
    ),
    path('logout/', views.logout_view, name='logout'),
]
