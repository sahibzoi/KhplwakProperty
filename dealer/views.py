from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum, Q
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django import forms
import csv
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Investor, PropertyItem, Transaction, Commission, Expense, Income
from django.views.decorators.cache import never_cache
from .forms import (
    InvestorForm,
    PropertyItemForm,
    TransactionForm,
    CommissionForm,
    ExpenseForm,
    IncomeForm
)

# ===================== DASHBOARD =====================

@login_required
@never_cache
def home(request):
    investor_count    = Investor.objects.count()
    property_count    = PropertyItem.objects.count()
    transaction_count = Transaction.objects.count()

    # property status counts
    available_count = PropertyItem.objects.filter(status='available').count()
    rented_count    = PropertyItem.objects.filter(status='rented').count()
    sold_count      = PropertyItem.objects.filter(status='sold').count()
    mortgaged_count = PropertyItem.objects.filter(status='mortgaged').count()

    # totals across ALL activity
    total_invested = Transaction.objects.filter(
        transaction_type__iexact='buy'
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_returned = Transaction.objects.filter(
        transaction_type__iexact='sell'
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_commissions = Commission.objects.aggregate(
        total=Sum('total_earned')
    )['total'] or 0

    context = {
        "investor_count": investor_count,
        "property_count": property_count,
        "transaction_count": transaction_count,

        "available_count": available_count,
        "rented_count": rented_count,
        "sold_count": sold_count,
        "mortgaged_count": mortgaged_count,

        "total_invested": total_invested,
        "total_returned": total_returned,
        "total_commissions": total_commissions,
    }
    return render(request, 'dealer/home.html', context)


# ===================== INVESTORS =====================

@login_required
@never_cache
def investor_list(request):
    investors = Investor.objects.all()
    return render(request, 'dealer/investor_list.html', {'investors': investors})


@login_required
@never_cache
def investor_create(request):
    if request.method == 'POST':
        form = InvestorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('investor_list')
    else:
        form = InvestorForm()
    return render(request, 'dealer/investor_form.html', {'form': form})


@login_required
@never_cache
def investor_edit(request, id):
    investor = get_object_or_404(Investor, id=id)
    if request.method == 'POST':
        form = InvestorForm(request.POST, instance=investor)
        if form.is_valid():
            form.save()
            return redirect('investor_list')
    else:
        form = InvestorForm(instance=investor)
    return render(request, 'dealer/investor_form.html', {'form': form})


@login_required
@never_cache
def investor_delete(request, id):
    investor = get_object_or_404(Investor, id=id)
    if request.method == 'POST':
        investor.delete()
        return redirect('investor_list')
    return render(request, 'dealer/investor_confirm_delete.html', {'investor': investor})


@login_required
@never_cache
def investor_detail(request, id):
    investor = get_object_or_404(Investor, id=id)
    transactions = Transaction.objects.filter(investor=investor).select_related('property_item')

    total_invested = transactions.filter(
        transaction_type__iexact='buy'
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_returned = transactions.filter(
        transaction_type__iexact='sell'
    ).aggregate(total=Sum('amount'))['total'] or 0

    net_result = total_returned - total_invested  # profit/loss for THIS investor

    context = {
        'investor': investor,
        'transactions': transactions,
        'total_invested': total_invested,
        'total_returned': total_returned,
        'net_result': net_result,
    }

    return render(request, 'dealer/investor_detail.html', context)


# ===================== PROPERTIES =====================

@login_required
@never_cache
def property_list(request):
    q = request.GET.get('q', '').strip()
    listing_type = request.GET.get('listing_type', '').strip()
    status = request.GET.get('status', '').strip()

    properties = PropertyItem.objects.all()

    if q:
        properties = properties.filter(
            Q(address__icontains=q) |
            Q(city__icontains=q) |
            Q(area_name__icontains=q)
        )

    if listing_type:
        properties = properties.filter(listing_type=listing_type)

    if status:
        properties = properties.filter(status=status)

    context = {
        'properties': properties,
        'q': q,
        'selected_listing_type': listing_type,
        'selected_status': status,
    }
    return render(request, 'dealer/property_list.html', context)


@login_required
@never_cache
def property_create(request):
    if request.method == 'POST':
        form = PropertyItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('property_list')
    else:
        form = PropertyItemForm()
    return render(request, 'dealer/property_form.html', {'form': form})


@login_required
@never_cache
def property_edit(request, id):
    prop = get_object_or_404(PropertyItem, id=id)
    if request.method == 'POST':
        form = PropertyItemForm(request.POST, instance=prop)
        if form.is_valid():
            form.save()
            return redirect('property_list')
    else:
        form = PropertyItemForm(instance=prop)
    return render(request, 'dealer/property_form.html', {'form': form})


@login_required
@never_cache
def property_delete(request, id):
    prop = get_object_or_404(PropertyItem, id=id)
    if request.method == 'POST':
        prop.delete()
        return redirect('property_list')
    return render(request, 'dealer/property_confirm_delete.html', {'prop': prop})


@login_required
@never_cache
def export_properties_csv(request):
    q = request.GET.get('q', '').strip()
    listing_type = request.GET.get('listing_type', '').strip()
    status = request.GET.get('status', '').strip()

    properties = PropertyItem.objects.all()

    if q:
        properties = properties.filter(
            Q(address__icontains=q) |
            Q(city__icontains=q) |
            Q(area_name__icontains=q)
        )
    if listing_type:
        properties = properties.filter(listing_type=listing_type)
    if status:
        properties = properties.filter(status=status)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="properties_export.csv"'
    writer = csv.writer(response)

    writer.writerow([
        'ID',
        'Address',
        'City',
        'Area',
        'Property Type',
        'Listing Type',
        'Status',
        'Size (Biswa)',
        'Bedrooms',
        'Bathrooms',
        'Kitchens',
        'Floor No',
        'Total Floors',
        'Parking Spaces',
        'Floor Area (sqft)',
        'Sale Price',
        'Rent Monthly',
        'Rent Deposit',
        'Mortgage Amount',
        'Mortgage Terms',
        'Owner Name',
        'Owner Contact',
        'Description',
    ])

    for p in properties:
        writer.writerow([
            p.id,
            p.address,
            p.city or '',
            p.area_name or '',
            p.property_type,
            p.get_listing_type_display(),
            p.status,
            p.size or '',
            p.bedrooms or '',
            p.bathrooms or '',
            p.kitchens or '',
            p.floor_no or '',
            p.total_floors or '',
            p.parking_spaces or '',
            p.floor_area_sqft or '',
            p.sale_price or '',
            p.rent_monthly or '',
            p.rent_deposit or '',
            p.mortgage_amount or '',
            (p.mortgage_terms or '').replace('\n', ' '),
            p.owner_name or '',
            p.owner_contact or '',
            (p.description or '').replace('\n', ' '),
        ])

    return response


# ===================== PROPERTY DETAIL DASHBOARD =====================

@login_required
@never_cache
def property_detail(request, id):
    prop = get_object_or_404(PropertyItem, id=id)

    transactions = (
        Transaction.objects
        .filter(property_item=prop)
        .select_related('investor')
        .order_by('-transaction_date')
    )

    commissions = (
        Commission.objects
        .filter(property_item=prop)
        .order_by('-created_at')
    )

    total_invested = transactions.filter(
        transaction_type__iexact='buy'
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_returned = transactions.filter(
        transaction_type__iexact='sell'
    ).aggregate(total=Sum('amount'))['total'] or 0

    net_result = total_returned - total_invested

    total_commission_earned = commissions.aggregate(
        total=Sum('total_earned')
    )['total'] or 0

    context = {
        "prop": prop,
        "total_invested": total_invested,
        "total_returned": total_returned,
        "net_result": net_result,
        "total_commission_earned": total_commission_earned,
        "transactions": transactions,
        "commissions": commissions,
    }

    return render(request, 'dealer/property_detail.html', context)


# ===================== COMMISSIONS =====================

@login_required
@never_cache
def commission_list(request):
    commissions = Commission.objects.select_related('property_item').order_by('-created_at')

    total_commission = commissions.aggregate(
        total=Sum('total_earned')
    )['total'] or 0

    context = {
        'commissions': commissions,
        'total_commission': total_commission,
    }
    return render(request, 'dealer/commission_list.html', context)


@login_required
@never_cache
def commission_create(request):
    """
    Add Commission.
    If ?property=<id> is present:
    - lock that property for this commission
    - hide property field in form
    - after save, return to that property dashboard
    """

    prop_id = request.GET.get('property')
    locked_property = None
    if prop_id:
        locked_property = get_object_or_404(PropertyItem, id=prop_id)

    if request.method == 'POST':
        form = CommissionForm(request.POST)

        if form.is_valid():
            obj = form.save(commit=False)

            if locked_property:
                obj.property_item = locked_property  # force it

            obj.save()

            if locked_property:
                return redirect('property_detail', id=locked_property.id)

            return redirect('commission_list')

        # on invalid form, if locked_property we keep it hidden
        if locked_property:
            form.fields['property_item'].initial = locked_property.id
            form.fields['property_item'].widget = forms.HiddenInput()

    else:
        form = CommissionForm()

        if locked_property:
            form.fields['property_item'].initial = locked_property.id
            form.fields['property_item'].widget = forms.HiddenInput()

    return render(
    request,
    'dealer/commission_form.html',   # ← use the file you already have
    {
        'form': form,
        'property_id': locked_property.id if locked_property else None,
    }
)


@login_required
@never_cache
def commission_edit(request, id):
    commission = get_object_or_404(Commission, id=id)

    if request.method == 'POST':
        form = CommissionForm(request.POST, instance=commission)
        if form.is_valid():
            form.save()
            return redirect('commission_list')
    else:
        form = CommissionForm(instance=commission)

    return render(
        request,
        'dealer/commission_form.html',
        {
            'form': form,
            'locked_property': None,
        }
    )


@login_required
@never_cache
def commission_delete(request, id):
    commission = get_object_or_404(Commission, id=id)
    if request.method == 'POST':
        commission.delete()
        return redirect('commission_list')
    return render(request, 'dealer/commission_confirm_delete.html', {'commission': commission})


# ===================== TRANSACTIONS =====================

@login_required
@never_cache
def transaction_list(request):
    transactions = (
        Transaction.objects
        .select_related('property_item', 'investor')
        .order_by('-transaction_date')
    )
    return render(request, 'dealer/transaction_list.html', {'transactions': transactions})


@login_required
@never_cache
def transaction_create(request):
    prop_id = request.GET.get('property')
    locked_property = None
    if prop_id:
        locked_property = get_object_or_404(PropertyItem, id=prop_id)

    if request.method == 'POST':
        form = TransactionForm(request.POST)

        if form.is_valid():
            obj = form.save(commit=False)

            if locked_property:
                obj.property_item = locked_property  # force selection

            obj.save()

            if locked_property:
                return redirect('property_detail', id=locked_property.id)

            return redirect('transaction_list')

        # form invalid -> keep locked property if we had one
        if locked_property:
            form.fields['property_item'].initial = locked_property.id
            form.fields['property_item'].widget = forms.HiddenInput()

    else:
        form = TransactionForm()

        if locked_property:
            form.fields['property_item'].initial = locked_property.id
            form.fields['property_item'].widget = forms.HiddenInput()

    return render(
        request,
        'dealer/transaction_form.html',
        {
            'form': form,
            'locked_property': locked_property,
        }
    )


@login_required
@never_cache
def transaction_edit(request, id):
    trans = get_object_or_404(Transaction, id=id)

    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=trans)
        if form.is_valid():
            form.save()
            return redirect('transaction_list')
    else:
        form = TransactionForm(instance=trans)

    return render(
        request,
        'dealer/transaction_form.html',
        {
            'form': form,
            'locked_property': None,
        }
    )


@login_required
@never_cache
def transaction_delete(request, id):
    trans = get_object_or_404(Transaction, id=id)
    if request.method == 'POST':
        trans.delete()
        return redirect('transaction_list')
    return render(request, 'dealer/transaction_confirm_delete.html', {'transaction': trans})


# ===================== EXPENSES =====================

@login_required
@never_cache
def expense_list(request):
    expenses = (
        Expense.objects
        .select_related('property_item')
        .order_by('-date', '-id')
    )

    total_expense = expenses.aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'expenses': expenses,
        'total_expense': total_expense,
    }
    return render(request, 'dealer/expense_list.html', context)


@login_required
@never_cache
def expense_create(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.created_by = request.user
            obj.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm()

    return render(request, 'dealer/expense_form.html', {'form': form})


@login_required
@never_cache
def expense_edit(request, id):
    expense = get_object_or_404(Expense, id=id)

    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense)

    return render(request, 'dealer/expense_form.html', {'form': form})


@login_required
@never_cache
def expense_delete(request, id):
    expense = get_object_or_404(Expense, id=id)

    if request.method == 'POST':
        expense.delete()
        return redirect('expense_list')

    return render(request, 'dealer/expense_confirm_delete.html', {'expense': expense})


# ===================== INCOME =====================

@login_required
@never_cache
def income_list(request):
    incomes = (
        Income.objects
        .select_related('property_item')
        .order_by('-date', '-id')
    )

    total_income = incomes.aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'incomes': incomes,
        'total_income': total_income,
    }
    return render(request, 'dealer/income_list.html', context)


@login_required
@never_cache
def income_create(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.created_by = request.user
            obj.save()
            return redirect('income_list')
    else:
        form = IncomeForm()

    return render(request, 'dealer/income_form.html', {'form': form})


@login_required
@never_cache
def income_edit(request, id):
    income = get_object_or_404(Income, id=id)

    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=income)
        if form.is_valid():
            form.save()
            return redirect('income_list')
    else:
        form = IncomeForm(instance=income)

    return render(request, 'dealer/income_form.html', {'form': form})


@login_required
@never_cache
def income_delete(request, id):
    income = get_object_or_404(Income, id=id)

    if request.method == 'POST':
        income.delete()
        return redirect('income_list')

    return render(request, 'dealer/income_confirm_delete.html', {'income': income})


# ===================== REPORTS / FINANCE =====================

@login_required
@never_cache
def finance_report(request):
    total_income = Income.objects.aggregate(total=Sum('amount'))['total'] or 0
    total_expense = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0
    net_balance = total_income - total_expense

    expense_by_category = (
        Expense.objects
        .values('category')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    income_by_source = (
        Income.objects
        .values('source')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    context = {
        'total_income': total_income,
        'total_expense': total_expense,
        'net_balance': net_balance,
        'expense_by_category': expense_by_category,
        'income_by_source': income_by_source,
    }
    return render(request, 'dealer/finance_report.html', context)


# ===================== BACKUP & TOOLS =====================

@login_required
@never_cache
def export_backup_csv(request):
    """
    Download a CSV snapshot of all core data:
    - Investors
    - Expenses
    - Income
    One file. Easy to keep offline or give to accountant.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="khplwak_backup.csv"'

    writer = csv.writer(response)

    # Investors
    writer.writerow(['=== INVESTORS ==='])
    writer.writerow([
        'id', 'full_name', 'surname', 'phone', 'location',
        'invested_amount', 'created_at'
    ])
    for inv in Investor.objects.all():
        writer.writerow([
            inv.id,
            getattr(inv, 'full_name', ''),
            getattr(inv, 'surname', ''),
            getattr(inv, 'phone', ''),
            getattr(inv, 'location', ''),
            getattr(inv, 'invested_amount', ''),
            getattr(inv, 'created_at', ''),
        ])

    writer.writerow([])

    # Expenses
    writer.writerow(['=== EXPENSES ==='])
    writer.writerow([
        'id', 'date', 'category', 'description', 'amount',
        'property_item', 'remarks'
    ])
    for e in Expense.objects.all():
        writer.writerow([
            e.id,
            e.date,
            e.category,
            e.description,
            e.amount,
            e.property_item.address if e.property_item else '',
            e.remarks or '',
        ])

    writer.writerow([])

    # Income
    writer.writerow(['=== INCOME ==='])
    writer.writerow([
        'id', 'date', 'source', 'description', 'amount',
        'property_item', 'remarks'
    ])
    for inc in Income.objects.all():
        writer.writerow([
            inc.id,
            inc.date,
            inc.source,
            inc.description,
            inc.amount,
            inc.property_item.address if inc.property_item else '',
            inc.remarks or '',
        ])

    return response


@login_required
@never_cache
def backup_dashboard(request):
    """
    Backup & Tools dashboard UI.
    Renders a page with:
    - Export all data CSV download
    - (Future) per-section exports
    - (Future) printable report
    """
    return render(request, 'dealer/backup_dashboard.html')


# ===================== AUTH =====================


def login_view(request):
    # Already logged in? Go to dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')

    next_url = request.GET.get('next') or request.POST.get('next') or 'dashboard'
    ctx = {'next': next_url, 'invalid': False}

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(next_url)

        # Show error via messages + fail-safe flag
        messages.error(request, "Invalid username or password.")
        ctx['invalid'] = True

    # IMPORTANT: point to the explicit template path to avoid conflicts
    return render(request, 'accounts/login.html', ctx)

@login_required
@never_cache

def logout_view(request):
    if request.method == 'POST':
        logout(request)
    return redirect('login')# dealer/views.py
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def login_view(request):
    # TEMP debug print (shows in runserver console)
    print(">>> LOGIN_VIEW HIT")

    if request.user.is_authenticated:
        return redirect('dashboard')

    next_url = request.GET.get('next') or request.POST.get('next') or 'dashboard'
    ctx = {'next': next_url, 'invalid': True}  # <-- FORCE TRUE for testing

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(next_url)

        messages.error(request, "Invalid username or password.")
        ctx['invalid'] = True

    # FORCE the specific template path (avoid any duplicate login.html)
    return render(request, 'accounts/login.html', ctx)

@login_required
@never_cache
def logout_view(request):
    if request.method == 'POST':
        logout(request)
    return redirect('login')
