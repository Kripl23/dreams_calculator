from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            messages.success(
                request, f'Account {username} registered succesfuly! You can login')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html')
