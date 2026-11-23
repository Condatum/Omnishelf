from django import forms

from .models import Folder, LibraryEntry, Tag

INPUT_CLASSES = (
    'w-full rounded-xl border border-shelf-border bg-shelf-bg px-3.5 py-2.5 '
    'text-sm text-slate-100 placeholder-slate-500 '
    'focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/40'
)

SELECT_CLASSES = (
    'w-full rounded-xl border border-shelf-border bg-shelf-bg px-3.5 py-2.5 '
    'text-sm text-slate-100 '
    'focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/40'
)


class LibraryEntryForm(forms.ModelForm):
    """Metadata override and Deep-Link URI form strictly scoped to request.user."""

    clear_cover_image = forms.BooleanField(
        required=False,
        label='Remove uploaded cover image',
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 rounded border-shelf-border bg-shelf-bg text-indigo-500 focus:ring-indigo-500/40',
        }),
    )

    class Meta:
        model = LibraryEntry
        fields = [
            'custom_title',
            'original_source_title',
            'current_uri',
            'chapter_label',
            'status',
            'folder',
            'tags',
            'custom_cover_image',
            'custom_cover_url',
            'notes',
        ]
        widgets = {
            'custom_title': forms.TextInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'e.g., Mother of Learning',
                'required': 'required',
                'autofocus': 'autofocus',
            }),
            'original_source_title': forms.TextInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'Optional original blog or aggregator title',
            }),
            'current_uri': forms.URLInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'https://www.royalroad.com/fiction/.../chapter/...',
                'required': 'required',
                'autocorrect': 'off',
                'autocapitalize': 'none',
                'spellcheck': 'false',
            }),
            'chapter_label': forms.TextInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'e.g., Ch. 42 or Arc 3 Pt 2',
            }),
            'status': forms.Select(attrs={'class': SELECT_CLASSES}),
            'folder': forms.Select(attrs={'class': SELECT_CLASSES}),
            'tags': forms.CheckboxSelectMultiple(attrs={
                'class': 'h-4 w-4 rounded border-shelf-border bg-shelf-bg text-indigo-500',
            }),
            'custom_cover_image': forms.FileInput(attrs={
                'class': (
                    'block w-full text-sm text-slate-300 '
                    'file:mr-3 file:rounded-lg file:border-0 file:bg-shelf-elevated '
                    'file:px-3 file:py-2 file:text-xs file:font-semibold file:text-slate-200 '
                    'hover:file:bg-slate-700'
                ),
                'accept': 'image/*',
            }),
            'custom_cover_url': forms.URLInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'https://example.com/high-res-cover.jpg',
                'autocorrect': 'off',
                'autocapitalize': 'none',
                'spellcheck': 'false',
            }),
            'notes': forms.Textarea(attrs={
                'class': INPUT_CLASSES,
                'rows': 3,
                'placeholder': 'Stopped right before the tournament finals...',
            }),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user is not None:
            self.fields['folder'].queryset = Folder.objects.filter(user=user)
            self.fields['tags'].queryset = Tag.objects.filter(user=user)
        else:
            self.fields['folder'].queryset = Folder.objects.none()
            self.fields['tags'].queryset = Tag.objects.none()
        self.fields['folder'].empty_label = 'No folder (Unfiled)'

    def save(self, commit=True):
        entry = super().save(commit=False)
        if self.cleaned_data.get('clear_cover_image') and not self.files.get('custom_cover_image'):
            if entry.custom_cover_image:
                entry.custom_cover_image.delete(save=False)
            entry.custom_cover_image = None
        if commit:
            entry.save()
            self.save_m2m()
        return entry
