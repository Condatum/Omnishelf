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
