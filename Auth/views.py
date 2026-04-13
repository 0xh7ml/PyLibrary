from django.shortcuts import render, redirect, resolve_url
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils.http import url_has_allowed_host_and_scheme

# Create your views here.
def _safe_next_url(request):
    next_url = request.POST.get('next') or request.GET.get('next')
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return resolve_url('home')


def login_view(request):
    target_url = _safe_next_url(request)

    if request.user.is_authenticated:
        return redirect(target_url)

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect(target_url)
        else:
            messages.error(request, 'Invalid credentials!')
    return render(request, 'auth/login.html')

def register_view(request):
    return render(request, 'auth/register.html')

@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, 'Logged out successfully!')
    return redirect('login')