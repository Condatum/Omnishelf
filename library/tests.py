from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from .models import Folder, LibraryEntry, ReadingSnapshot, ReadingStatus, Tag

User = get_user_model()


class BaseShellTests(TestCase):
    """Verify the base dark-mode UI shell and root landing view."""

    def test_home_view_renders_base_shell(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'OmniShelf')
        self.assertContains(response, 'color-scheme')
        self.assertContains(response, 'htmx.org')
        self.assertContains(response, 'alpinejs')


class TaxonomyModelTests(TestCase):
    """Verify user-scoped Folder, Tag, and ReadingStatus taxonomy models."""

    def setUp(self):
        self.user_a = User.objects.create_user(username='reader_a', password='StrongPassword123!')
        self.user_b = User.objects.create_user(username='reader_b', password='StrongPassword123!')

    def test_reading_status_choices(self):
        expected = {'ACTIVE', 'ON_HOLD', 'BINGE_READY', 'HIATUS', 'COMPLETED'}
        self.assertEqual(set(ReadingStatus.values), expected)

    def test_folder_unique_per_user_but_allowed_across_users(self):
        Folder.objects.create(user=self.user_a, name='Progression Fantasy', sort_order=1)
        Folder.objects.create(user=self.user_b, name='Progression Fantasy', sort_order=1)

        with self.assertRaises(IntegrityError):
            Folder.objects.create(user=self.user_a, name='Progression Fantasy')

    def test_tag_auto_slugifies_and_scopes_to_user(self):
        tag = Tag.objects.create(user=self.user_a, name='Time Loop')
        self.assertEqual(tag.slug, 'time-loop')

        tag_b = Tag.objects.create(user=self.user_b, name='Time Loop')
        self.assertEqual(tag_b.slug, 'time-loop')

        with self.assertRaises(IntegrityError):
            Tag.objects.create(user=self.user_a, name='Time Loop')


class LibraryEntryAndSnapshotTests(TestCase):
    """Verify LibraryEntry domain parsing, ReadingSnapshot history, and cascade rules."""

    def setUp(self):
        self.user = User.objects.create_user(username='shelf_owner', password='StrongPassword123!')
        self.folder = Folder.objects.create(user=self.user, name='Sci-Fi')
        self.tag = Tag.objects.create(user=self.user, name='Hard Sci-Fi')

    def test_source_domain_auto_extracted_on_save(self):
        entry = LibraryEntry.objects.create(
            user=self.user,
            custom_title='The Last Starlight',
            current_uri='https://www.royalroad.com/fiction/12345/chapter/42',
            chapter_label='Ch. 42',
            folder=self.folder,
        )
        entry.tags.add(self.tag)
        self.assertEqual(entry.source_domain, 'royalroad.com')

        entry.current_uri = 'https://reddit.com/r/HFY/comments/abc/ch_43'
        entry.save()
        self.assertEqual(entry.source_domain, 'reddit.com')

    def test_reading_snapshot_history_and_cascade(self):
        entry = LibraryEntry.objects.create(
            user=self.user,
            custom_title='Chronicles of Void',
            current_uri='https://example.com/ch-1',
            chapter_label='Ch. 1',
        )
        snap = ReadingSnapshot.objects.create(
            entry=entry,
            uri='https://example.com/ch-1',
            chapter_label='Ch. 1',
            notes='Started arc 1',
        )
        self.assertEqual(entry.snapshots.count(), 1)
        self.assertEqual(entry.snapshots.first(), snap)

        entry.delete()
        self.assertEqual(ReadingSnapshot.objects.count(), 0)

    def test_deleting_folder_sets_entry_folder_null(self):
        entry = LibraryEntry.objects.create(
            user=self.user,
            custom_title='Orbital Drift',
            current_uri='https://example.com/ch-5',
            folder=self.folder,
        )
        self.folder.delete()
        entry.refresh_from_db()
        self.assertIsNone(entry.folder)
