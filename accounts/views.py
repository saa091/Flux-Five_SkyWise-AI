from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard') if request.user.is_staff else redirect('profil')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Selamat datang, {user.first_name or user.username}! 👋')
            if user.is_staff:
                return redirect('dashboard')
            next_url = request.GET.get('next', 'profil')
            return redirect(next_url)
        else:
            messages.error(request, 'Username atau password salah!')
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'Berhasil logout. Sampai jumpa!')
    return redirect('index')


class CustomPasswordResetView(PasswordResetView):
    def form_valid(self, form):
        email = form.cleaned_data['email']
        users = list(form.get_users(email))
        if users:
            user = users[0]
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            return redirect('password_reset_confirm', uidb64=uid, token=token)
        # Email gak ketemu di DB — tetep redirect biar gak ketauan email valid/gak
        return redirect('password_reset_confirm', uidb64='x', token='x')