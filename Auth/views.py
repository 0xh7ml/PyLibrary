from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return render(request, 'auth/login.html', {'messages': [{'level': 'success', 'message': 'Login successful!'}]})
        else:
            return render(request, 'auth/login.html', {'messages': [{'level': 'error', 'message': 'Invalid credentials!'}]})
    return render(request, 'auth/login.html')

def register_view(request):
    return render(request, 'auth/register.html')

def logout_view(request):
    logout(request)
    return render(request, 'auth/login.html', {'messages': [{'level': 'info', 'message': 'Logged out successfully!'}]})