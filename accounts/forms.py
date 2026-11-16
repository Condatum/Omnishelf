from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import CustomUser

INPUT_CLASSES = (
    'w-full rounded-xl border border-shelf-border bg-shelf-bg px-3.5 py-2.5 '
    'text-sm text-slate-100 placeholder-slate-500 '
    'focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/40'
)


class OmniShelfUserCreationForm(UserCreationForm):
    """Registration form with modern-web-guidance autofill and accessibility attributes."""

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': INPUT_CLASSES,
            'placeholder': 'reader@example.com',
            'autocomplete': 'email',
            'spellcheck': 'false',
            'required': 'required',
        }),
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': INPUT_CLASSES,
            'placeholder': 'Choose a username',
            'autocomplete': 'username',
            'spellcheck': 'false',
            'autocorrect': 'off',
            'autocapitalize': 'off',
            'required': 'required',
        })
        self.fields['password1'].widget.attrs.update({
            'class': INPUT_CLASSES,
            'placeholder': 'Create a strong password',
            'autocomplete': 'new-password',
            'required': 'required',
        })
        self.fields['password2'].widget.attrs.update({
            'class': INPUT_CLASSES,
            'placeholder': 'Confirm your password',
            'autocomplete': 'new-password',
            'required': 'required',
        })


class OmniShelfAuthenticationForm(AuthenticationForm):
    """Sign-in form with modern-web-guidance autofill attributes."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': INPUT_CLASSES,
            'placeholder': 'Enter your username',
            'autocomplete': 'username',
            'spellcheck': 'false',
            'autocorrect': 'off',
            'autocapitalize': 'off',
            'required': 'required',
        })
        self.fields['password'].widget.attrs.update({
            'class': INPUT_CLASSES,
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password',
            'required': 'required',
        })
