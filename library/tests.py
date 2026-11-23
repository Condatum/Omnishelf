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


class LibraryEntryCrudModalTests(TestCase):
    """Verify HTMX story creation, metadata customization, cover uploads, and CRUD isolation."""

    @classmethod
    def setUpTestData(cls):
        cls.user_a = User.objects.create_user(username='crud_a', password='StrongPassword123!')
        cls.user_b = User.objects.create_user(username='crud_b', password='StrongPassword123!')
        cls.folder_a = Folder.objects.create(user=cls.user_a, name='Cultivation')
        cls.tag_a = Tag.objects.create(user=cls.user_a, name='Regression')

    def _make_test_image(self):
        from io import BytesIO
        from PIL import Image
        from django.core.files.uploadedfile import SimpleUploadedFile

        buf = BytesIO()
        Image.new('RGB', (120, 160), color=(99, 102, 241)).save(buf, format='PNG')
        return SimpleUploadedFile('cover.png', buf.getvalue(), content_type='image/png')

    def test_htmx_create_story_with_custom_cover_upload(self):
        import shutil
        import tempfile
        from django.test import override_settings

        tmp_media = tempfile.mkdtemp()
        try:
            with override_settings(MEDIA_ROOT=tmp_media):
                self.client.force_login(self.user_a)
                response = self.client.post(
                    reverse('library:entry_create'),
                    {
                        'custom_title': 'Chronicles of the Spire',
                        'original_source_title': 'spire-novel-raw-blog',
                        'current_uri': 'https://www.royalroad.com/fiction/999/chapter/14',
                        'chapter_label': 'Ch. 14',
                        'status': ReadingStatus.BINGE_READY,
                        'folder': str(self.folder_a.pk),
                        'tags': [str(self.tag_a.pk)],
                        'custom_cover_image': self._make_test_image(),
                        'notes': 'Stopped right before the tournament finals.',
                    },
                    HTTP_HX_REQUEST='true',
                )
                self.assertEqual(response.status_code, 200)
                self.assertIn('closeModal', response['HX-Trigger'])
                self.assertContains(response, 'Chronicles of the Spire')
                self.assertContains(response, 'Stopped right before the tournament finals.')

                entry = LibraryEntry.objects.get(user=self.user_a, custom_title='Chronicles of the Spire')
                self.assertTrue(bool(entry.custom_cover_image))
                self.assertIn('covers/', entry.cover_src)
                self.assertEqual(entry.snapshots.count(), 1)
                self.assertContains(response, entry.cover_src)
        finally:
            shutil.rmtree(tmp_media, ignore_errors=True)

    def test_htmx_update_and_delete_entry(self):
        entry = LibraryEntry.objects.create(
            user=self.user_a,
            custom_title='Generic Blog Post #1',
            current_uri='https://example.com/ch-1',
            chapter_label='Ch. 1',
        )
        self.client.force_login(self.user_a)

        update_resp = self.client.post(
            reverse('library:entry_update', kwargs={'pk': entry.pk}),
            {
                'custom_title': 'Clean Custom Alias',
                'original_source_title': 'Generic Blog Post #1',
                'current_uri': 'https://example.com/ch-2',
                'chapter_label': 'Ch. 2',
                'status': ReadingStatus.ACTIVE,
                'custom_cover_url': 'https://example.com/custom-art.jpg',
                'notes': 'Updated context note',
            },
            HTTP_HX_REQUEST='true',
        )
        self.assertEqual(update_resp.status_code, 200)
        entry.refresh_from_db()
        self.assertEqual(entry.custom_title, 'Clean Custom Alias')
        self.assertEqual(entry.cover_src, 'https://example.com/custom-art.jpg')

        delete_resp = self.client.post(
            reverse('library:entry_delete', kwargs={'pk': entry.pk}),
            HTTP_HX_REQUEST='true',
        )
        self.assertEqual(delete_resp.status_code, 200)
        self.assertFalse(LibraryEntry.objects.filter(pk=entry.pk).exists())

    def test_cross_user_crud_isolation_enforced(self):
        entry_a = LibraryEntry.objects.create(
            user=self.user_a,
            custom_title='User A Private Novel',
            current_uri='https://example.com/private-ch-1',
        )
        self.client.force_login(self.user_b)

        # User B cannot view, edit, or delete User A's entry
        self.assertEqual(
            self.client.get(reverse('library:entry_update', kwargs={'pk': entry_a.pk})).status_code,
            404,
        )
        self.assertEqual(
            self.client.post(
                reverse('library:entry_update', kwargs={'pk': entry_a.pk}),
                {'custom_title': 'Hacked', 'current_uri': 'https://evil.com', 'status': ReadingStatus.ACTIVE},
            ).status_code,
            404,
        )
        self.assertEqual(
            self.client.post(reverse('library:entry_delete', kwargs={'pk': entry_a.pk})).status_code,
            404,
        )
        entry_a.refresh_from_db()
        self.assertEqual(entry_a.custom_title, 'User A Private Novel')

        # User B cannot bind User A's folder when creating an entry
        bad_create = self.client.post(
            reverse('library:entry_create'),
            {
                'custom_title': 'User B Story',
                'current_uri': 'https://example.com/b-ch-1',
                'status': ReadingStatus.ACTIVE,
                'folder': str(self.folder_a.pk),
            },
            HTTP_HX_REQUEST='true',
        )
        self.assertEqual(bad_create.status_code, 200)
        self.assertFalse(LibraryEntry.objects.filter(user=self.user_b, custom_title='User B Story').exists())


