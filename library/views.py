from django.shortcuts import render


def home_view(request):
    """Render the OmniShelf Grand Library landing/dashboard shell."""
    return render(request, 'library/home.html')
