from django.apps import apps
from django.utils import timezone


BACKUP_SCHEMA_VERSION = 'omnishelf_backup_v1'


def _get_model_if_exists(app_label: str, model_name: str):
    try:
        return apps.get_model(app_label, model_name)
    except LookupError:
        return None


def export_user_library_json(user) -> dict:
    """Serialize user profile and library metadata/URI history into a portable dict."""
    folders_data = []
    tags_data = []
    entries_data = []

    Folder = _get_model_if_exists('library', 'Folder')
    Tag = _get_model_if_exists('library', 'Tag')
    LibraryEntry = _get_model_if_exists('library', 'LibraryEntry')

    if Folder is not None:
        for folder in Folder.objects.filter(user=user).order_by('sort_order', 'name'):
            folders_data.append({
                'name': folder.name,
                'icon': getattr(folder, 'icon', ''),
                'color_hex': getattr(folder, 'color_hex', ''),
                'sort_order': getattr(folder, 'sort_order', 0),
            })

    if Tag is not None:
        for tag in Tag.objects.filter(user=user).order_by('name'):
            tags_data.append({
                'name': tag.name,
                'slug': tag.slug,
                'color_hex': getattr(tag, 'color_hex', ''),
            })

    if LibraryEntry is not None:
        for entry in LibraryEntry.objects.filter(user=user).prefetch_related('tags', 'snapshots'):
            snapshots_data = []
            if hasattr(entry, 'snapshots'):
                for snap in entry.snapshots.all().order_by('created_at'):
                    snapshots_data.append({
                        'uri': snap.uri,
                        'chapter_label': getattr(snap, 'chapter_label', ''),
                        'notes': getattr(snap, 'notes', ''),
                        'created_at': snap.created_at.isoformat() if snap.created_at else None,
                    })
            entries_data.append({
                'custom_title': entry.custom_title,
                'original_source_title': entry.original_source_title,
                'custom_cover_url': entry.custom_cover_url,
                'current_uri': entry.current_uri,
                'source_domain': entry.source_domain,
                'chapter_label': entry.chapter_label,
                'status': entry.status,
                'folder_name': entry.folder.name if entry.folder else None,
                'tag_names': list(entry.tags.values_list('name', flat=True)),
                'notes': entry.notes,
                'last_read_at': entry.last_read_at.isoformat() if entry.last_read_at else None,
                'snapshots': snapshots_data,
            })

    return {
        'schema_version': BACKUP_SCHEMA_VERSION,
        'exported_at': timezone.now().isoformat(),
        'user': {
            'id': str(user.pk),
            'username': user.username,
            'email': user.email,
        },
        'folders': folders_data,
        'tags': tags_data,
        'entries': entries_data,
    }


def import_user_library_json(user, payload: dict) -> dict:
    """Safely restore folders, tags, and library entries without duplicating records."""
    if not isinstance(payload, dict) or payload.get('schema_version') != BACKUP_SCHEMA_VERSION:
        raise ValueError('Unsupported or invalid OmniShelf backup JSON format.')

    stats = {'folders_created': 0, 'tags_created': 0, 'entries_created': 0, 'entries_skipped': 0}

    Folder = _get_model_if_exists('library', 'Folder')
    Tag = _get_model_if_exists('library', 'Tag')
    LibraryEntry = _get_model_if_exists('library', 'LibraryEntry')
    ReadingSnapshot = _get_model_if_exists('library', 'ReadingSnapshot')

    folder_map = {}
    if Folder is not None:
        for item in payload.get('folders', []):
            name = (item.get('name') or '').strip()
            if not name:
                continue
            folder, created = Folder.objects.get_or_create(
                user=user,
                name=name,
                defaults={
                    'icon': item.get('icon', ''),
                    'color_hex': item.get('color_hex', '#6366f1'),
                    'sort_order': item.get('sort_order', 0),
                },
            )
            folder_map[name] = folder
            if created:
                stats['folders_created'] += 1

    tag_map = {}
    if Tag is not None:
        for item in payload.get('tags', []):
            name = (item.get('name') or '').strip()
            if not name:
                continue
            tag, created = Tag.objects.get_or_create(
                user=user,
                name=name,
                defaults={'color_hex': item.get('color_hex', '#6366f1')},
            )
            tag_map[name] = tag
            if created:
                stats['tags_created'] += 1

    if LibraryEntry is not None:
        for item in payload.get('entries', []):
            current_uri = (item.get('current_uri') or '').strip()
            custom_title = (item.get('custom_title') or '').strip()
            if not current_uri or not custom_title:
                continue

            if LibraryEntry.objects.filter(user=user, current_uri=current_uri).exists():
                stats['entries_skipped'] += 1
                continue

            folder_obj = folder_map.get(item.get('folder_name'))
            entry = LibraryEntry.objects.create(
                user=user,
                custom_title=custom_title,
                original_source_title=item.get('original_source_title', ''),
                custom_cover_url=item.get('custom_cover_url', ''),
                current_uri=current_uri,
                chapter_label=item.get('chapter_label', ''),
                status=item.get('status', 'ACTIVE'),
                folder=folder_obj,
                notes=item.get('notes', ''),
            )
            for tag_name in item.get('tag_names', []):
                if tag_name in tag_map:
                    entry.tags.add(tag_map[tag_name])

            if ReadingSnapshot is not None:
                for snap in item.get('snapshots', []):
                    snap_uri = (snap.get('uri') or '').strip()
                    if snap_uri:
                        ReadingSnapshot.objects.get_or_create(
                            entry=entry,
                            uri=snap_uri,
                            chapter_label=snap.get('chapter_label', ''),
                            defaults={'notes': snap.get('notes', '')},
                        )

            stats['entries_created'] += 1

    return stats
