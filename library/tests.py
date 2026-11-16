from django.test import TestCase
from django.urls import reverse


class BaseShellTests(TestCase):
    """Verify the base dark-mode UI shell and root landing view."""

    def test_home_view_renders_base_shell(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'OmniShelf')
        self.assertContains(response, 'color-scheme')
        self.assertContains(response, 'htmx.org')
        self.assertContains(response, 'alpinejs')
