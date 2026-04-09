from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.http import require_POST

# Create your views here.
def login_view(request):
    if request.user.is_authenticated:
        return redirect(request.GET.get('next') or 'home')

    if request.method == "POST":
        next_url = request.POST.get('next')
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect(next_url or 'home')
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