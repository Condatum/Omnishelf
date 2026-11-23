from django import forms


class FreezeSnapshotForm(forms.Form):
    """Validate manual State-Capture ('Freeze Snapshot') URI and progress updates."""

    uri = forms.URLField(
        max_length=2000,
        required=True,
        widget=forms.URLInput(attrs={
            'placeholder': 'Paste current chapter URL...',
            'autocorrect': 'off',
            'autocapitalize': 'none',
            'spellcheck': 'false',
            'required': 'required',
        }),
    )
    chapter_label = forms.CharField(
        max_length=120,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ch. 42',
        }),
    )
    notes = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Quick context reminder (optional)...',
        }),
    )
