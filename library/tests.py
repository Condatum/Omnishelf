from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from .models import Folder, ReadingStatus, Tag

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
