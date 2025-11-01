from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if not user.is_active:
                messages.error(request, "Your account is inactive. Contact the administrator.")
                return render(request, 'accounts/login.html', {'next': request.POST.get('next', '')})
            login(request, user)
            return redirect(request.POST.get('next') or 'home')

        # invalid credentials
        messages.error(request, "Invalid username or password.")
        return render(request, 'accounts/login.html', {'next': request.POST.get('next', '')})

    # GET
    return render(request, 'accounts/login.html', {'next': request.GET.get('next', '')})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # respect ?next=... if present
            nxt = request.POST.get('next') or request.GET.get('next')
            return redirect(nxt or 'home')

        # wrong credentials -> show on same page
        messages.error(request, 'Invalid username or password.')

    # GET or failed POST
    return render(request, 'accounts/login.html', {
        'next': request.GET.get('next', ''),
    })