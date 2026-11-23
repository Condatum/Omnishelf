from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from library.models import LibraryEntry

User = get_user_model()


class ViewportReaderTests(TestCase):
    """Verify Sandboxed Viewport Reader, Deep-Link Resume launch, last_read_at update, and isolation."""

    @classmethod
    def setUpTestData(cls):
        cls.user_a = User.objects.create_user(username='reader_user_a', password='StrongPassword123!')
        cls.user_b = User.objects.create_user(username='reader_user_b', password='StrongPassword123!')

    def test_viewport_requires_authentication(self):
        entry = LibraryEntry.objects.create(
            user=self.user_a,
            custom_title='Auth Gated Serial',
            current_uri='https://www.royalroad.com/fiction/1/chapter/1',
        )
        response = self.client.get(reverse('reader:viewport', kwargs={'entry_id': entry.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('accounts:login'), response.url)

    def test_deep_link_launch_updates_last_read_at_and_renders_sandbox(self):
        old_time = timezone.now() - timedelta(days=5)
        entry = LibraryEntry.objects.create(
            user=self.user_a,
            custom_title='Wandering Star',
            current_uri='https://www.royalroad.com/fiction/777/chapter/88',
            chapter_label='Ch. 88',
            notes='Just crossed the northern gate.',
            last_read_at=old_time,
        )

        self.client.force_login(self.user_a)
        response = self.client.get(reverse('reader:viewport', kwargs={'entry_id': entry.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'sandbox="allow-scripts allow-same-origin allow-forms allow-popups"')
        self.assertContains(response, 'https://www.royalroad.com/fiction/777/chapter/88')
        self.assertContains(response, 'External Tab Fallback')
        self.assertContains(response, 'Just crossed the northern gate.')

        entry.refresh_from_db()
        self.assertGreater(entry.last_read_at, old_time + timedelta(days=4))

    def test_viewport_enforces_user_isolation(self):
        old_time = timezone.now() - timedelta(days=2)
        entry_a = LibraryEntry.objects.create(
            user=self.user_a,
            custom_title='Private Story A',
            current_uri='https://example.com/private-ch-10',
            last_read_at=old_time,
        )
        self.client.force_login(self.user_b)
        response = self.client.get(reverse('reader:viewport', kwargs={'entry_id': entry_a.pk}))
        self.assertEqual(response.status_code, 404)

        entry_a.refresh_from_db()
        self.assertEqual(entry_a.last_read_at, old_time)


class StateCaptureSnapshotTests(TestCase):
    """Verify Freeze Snapshot creation, domain re-evaluation, smart chapter increment, and rollback."""

    @classmethod
    def setUpTestData(cls):
        cls.user_a = User.objects.create_user(username='snap_a', password='StrongPassword123!')
        cls.user_b = User.objects.create_user(username='snap_b', password='StrongPassword123!')

    def test_smart_chapter_increment_regex(self):
        from .utils import increment_chapter_label

        self.assertEqual(increment_chapter_label('Ch. 41'), 'Ch. 42')
        self.assertEqual(increment_chapter_label('Chapter 009'), 'Chapter 010')
        self.assertEqual(increment_chapter_label('Arc 4 Pt 2'), 'Arc 4 Pt 3')
        self.assertEqual(increment_chapter_label(''), 'Ch. 1')
        self.assertEqual(increment_chapter_label('Prologue'), 'Prologue 2')

    def test_freeze_snapshot_updates_entry_domain_and_logs_history(self):
        from library.models import ReadingSnapshot

        entry = LibraryEntry.objects.create(
            user=self.user_a,
            custom_title='Realm Wanderer',
            current_uri='https://www.royalroad.com/fiction/100/chapter/41',
            chapter_label='Ch. 41',
            notes='Before the guild trial.',
        )
        initial_snap = ReadingSnapshot.objects.create(
            entry=entry,
            uri=entry.current_uri,
            chapter_label='Ch. 41',
            notes='Before the guild trial.',
        )

        self.client.force_login(self.user_a)
        freeze_resp = self.client.post(
            reverse('reader:freeze_snapshot', kwargs={'entry_id': entry.pk}),
            {
                'source': 'hud',
                'uri': 'https://www.reddit.com/r/HFY/comments/xyz/chapter_42',
                'chapter_label': 'Ch. 41',
                'increment_chapter': '1',
                'notes': 'Finished guild trial cliffhanger!',
            },
            HTTP_HX_REQUEST='true',
        )
        self.assertEqual(freeze_resp.status_code, 200)
        self.assertContains(freeze_resp, 'Snapshot Frozen at Ch. 42')
        self.assertIn('snapshotFrozen', freeze_resp['HX-Trigger'])

        entry.refresh_from_db()
        self.assertEqual(entry.chapter_label, 'Ch. 42')
        self.assertEqual(entry.source_domain, 'reddit.com')
        self.assertEqual(entry.current_uri, 'https://www.reddit.com/r/HFY/comments/xyz/chapter_42')
        self.assertEqual(entry.notes, 'Finished guild trial cliffhanger!')
        self.assertEqual(entry.snapshots.count(), 2)

        # Roll back to initial snapshot (Ch. 41 on royalroad.com)
        rollback_resp = self.client.post(
            reverse('reader:rollback_snapshot', kwargs={'entry_id': entry.pk, 'snapshot_id': initial_snap.pk}),
            HTTP_HX_REQUEST='true',
        )
        self.assertEqual(rollback_resp.status_code, 200)
        self.assertContains(rollback_resp, 'Rolled back to Ch. 41')

        entry.refresh_from_db()
        self.assertEqual(entry.chapter_label, 'Ch. 41')
        self.assertEqual(entry.source_domain, 'royalroad.com')
        self.assertEqual(entry.current_uri, 'https://www.royalroad.com/fiction/100/chapter/41')
        self.assertEqual(entry.snapshots.count(), 3)

    def test_quick_card_snapshot_modal_and_user_isolation(self):
        from library.models import ReadingSnapshot

        entry = LibraryEntry.objects.create(
            user=self.user_a,
            custom_title='Card Quick Snap Story',
            current_uri='https://example.com/ch-10',
            chapter_label='Ch. 10',
        )
        snap = ReadingSnapshot.objects.create(
            entry=entry,
            uri=entry.current_uri,
            chapter_label='Ch. 10',
        )

        # Cross-tenant isolation: user_b gets 404 on quick modal, freeze, and rollback
        self.client.force_login(self.user_b)
        self.assertEqual(
            self.client.get(reverse('reader:quick_snapshot_modal', kwargs={'entry_id': entry.pk}), HTTP_HX_REQUEST='true').status_code,
            404,
        )
        self.assertEqual(
            self.client.post(
                reverse('reader:freeze_snapshot', kwargs={'entry_id': entry.pk}),
                {'uri': 'https://evil.com/ch-99', 'chapter_label': 'Ch. 99'},
            ).status_code,
            404,
        )
        self.assertEqual(
            self.client.post(
                reverse('reader:rollback_snapshot', kwargs={'entry_id': entry.pk, 'snapshot_id': snap.pk}),
            ).status_code,
            404,
        )

        # Owner updates snapshot via quick card modal
        self.client.force_login(self.user_a)
        modal_resp = self.client.get(
            reverse('reader:quick_snapshot_modal', kwargs={'entry_id': entry.pk}),
            HTTP_HX_REQUEST='true',
        )
        self.assertEqual(modal_resp.status_code, 200)
        self.assertContains(modal_resp, '+1 Chapter')

        card_freeze = self.client.post(
            reverse('reader:freeze_snapshot', kwargs={'entry_id': entry.pk}),
            {
                'source': 'card',
                'uri': 'https://example.com/ch-11',
                'chapter_label': 'Ch. 11',
                'notes': 'Updated from card',
            },
            HTTP_HX_REQUEST='true',
        )
        self.assertEqual(card_freeze.status_code, 200)
        self.assertIn('closeModal', card_freeze['HX-Trigger'])
        self.assertContains(card_freeze, 'Ch. 11')

