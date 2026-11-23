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


class GrandLibraryDashboardTests(TestCase):
    """Verify GrandLibraryView rendering, empty state, 15+ cards, and user isolation."""

    def setUp(self):
        self.user_a = User.objects.create_user(username='dash_a', password='StrongPassword123!')
        self.user_b = User.objects.create_user(username='dash_b', password='StrongPassword123!')

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('library:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('accounts:login'), response.url)

    def test_dashboard_empty_state_onboarding(self):
        self.client.force_login(self.user_a)
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your Grand Library is empty')
        self.assertEqual(response.context['total_count'], 0)

    def test_dashboard_renders_fifteen_plus_entries_with_isolation(self):
        folder = Folder.objects.create(user=self.user_a, name='Favorites')
        tag = Tag.objects.create(user=self.user_a, name='LitRPG')

        statuses = list(ReadingStatus.values)
        for idx in range(1, 17):
            entry = LibraryEntry.objects.create(
                user=self.user_a,
                custom_title=f'Serial Saga #{idx}',
                current_uri=f'https://www.royalroad.com/fiction/{idx}/chapter/{idx * 10}',
                chapter_label=f'Ch. {idx * 10}',
                status=statuses[idx % len(statuses)],
                folder=folder,
                custom_cover_url='https://example.com/cover.jpg' if idx % 2 == 0 else '',
                notes=f'Stopped right before arc {idx}.',
            )
            entry.tags.add(tag)

        # Entry owned by user_b must never appear on user_a's dashboard
        LibraryEntry.objects.create(
            user=self.user_b,
            custom_title='Secret Private Story B',
            current_uri='https://reddit.com/r/HFY/comments/secret/ch1',
            chapter_label='Ch. 1',
        )

        self.client.force_login(self.user_a)
        response = self.client.get(reverse('library:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_count'], 16)
        self.assertContains(response, 'Serial Saga #1')
        self.assertContains(response, 'Serial Saga #16')
        self.assertContains(response, 'royalroad.com')
        self.assertContains(response, 'Deep-Link Resume')
        self.assertContains(response, 'Ch. 160')
        self.assertNotContains(response, 'Secret Private Story B')

