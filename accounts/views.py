from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import OmniShelfAuthenticationForm, OmniShelfUserCreationForm


def register_view(request):
    """Register a new CustomUser and log them in immediately."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = OmniShelfUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to OmniShelf, {user.username}!')
            return redirect('home')
    else:
        form = OmniShelfUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """Authenticate an existing CustomUser."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = OmniShelfAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}.')
            next_url = request.GET.get('next') or 'home'
            return redirect(next_url)
    else:
        form = OmniShelfAuthenticationForm(request)

    return render(request, 'accounts/login.html', {'form': form})


@login_required
@require_POST
def logout_view(request):
    """Sign out the current user via POST request."""
    logout(request)
    messages.info(request, 'You have been signed out.')
    return redirect('home')
