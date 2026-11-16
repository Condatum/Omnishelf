import json

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .backup import export_user_library_json, import_user_library_json
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


@login_required
def settings_view(request):
    """Account settings & Data Sovereignty backup/restore center."""
    return render(request, 'accounts/settings.html')


@login_required
def export_library_view(request):
    """Export the authenticated user's library metadata as a timestamped JSON file."""
    data = export_user_library_json(request.user)
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    filename = f'omnishelf_backup_{request.user.username}_{timestamp}.json'
    response = HttpResponse(
        json.dumps(data, indent=2),
        content_type='application/json',
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
@require_POST
def import_library_view(request):
    """Import a portable JSON backup file without duplicating records."""
    uploaded_file = request.FILES.get('backup_file')
    if not uploaded_file:
        messages.error(request, 'Please select a JSON backup file to import.')
        return redirect('accounts:settings')

    try:
        payload = json.loads(uploaded_file.read().decode('utf-8'))
        stats = import_user_library_json(request.user, payload)
        messages.success(
            request,
            f"Backup restored: {stats['entries_created']} entries, "
            f"{stats['folders_created']} folders, {stats['tags_created']} tags added "
            f"({stats['entries_skipped']} duplicates skipped).",
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        messages.error(request, f'Import failed: {exc}')

    return redirect('accounts:settings')
