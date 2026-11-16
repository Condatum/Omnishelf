import json
import uuid

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .backup import BACKUP_SCHEMA_VERSION

User = get_user_model()


class CustomUserAuthTests(TestCase):
    """Verify UUID-backed CustomUser model and encapsulated auth workflows."""

    def test_custom_user_uses_uuid_primary_key(self):
        user = User.objects.create_user(
            username='reader1',
            email='reader1@example.com',
            password='StrongPassword123!',
        )
        self.assertIsInstance(user.pk, uuid.UUID)

    def test_register_creates_user_and_logs_in(self):
        response = self.client.post(
            reverse('accounts:register'),
            {
                'username': 'newreader',
                'email': 'newreader@example.com',
                'password1': 'StrongPassword123!',
                'password2': 'StrongPassword123!',
            },
        )
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(User.objects.filter(username='newreader').exists())
        self.assertIn('_auth_user_id', self.client.session)

    def test_login_and_logout_workflow(self):
        User.objects.create_user(
            username='alice',
            email='alice@example.com',
            password='StrongPassword123!',
        )
        login_response = self.client.post(
            reverse('accounts:login'),
            {'username': 'alice', 'password': 'StrongPassword123!'},
        )
        self.assertRedirects(login_response, reverse('home'))
        self.assertIn('_auth_user_id', self.client.session)

        # GET logout should not be allowed (405 Method Not Allowed)
        get_logout = self.client.get(reverse('accounts:logout'))
        self.assertEqual(get_logout.status_code, 405)

        # POST logout signs out cleanly
        post_logout = self.client.post(reverse('accounts:logout'))
        self.assertRedirects(post_logout, reverse('home'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_invalid_login_renders_error(self):
        response = self.client.post(
            reverse('accounts:login'),
            {'username': 'nonexistent', 'password': 'wrongpassword'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a correct username and password')

    def test_logout_requires_authentication(self):
        response = self.client.post(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('accounts:login'), response.url)


class DataSovereigntyBackupTests(TestCase):
    """Verify JSON library export and import endpoints."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='backup_user',
            email='backup@example.com',
            password='StrongPassword123!',
        )

    def test_export_requires_authentication(self):
        response = self.client.get(reverse('accounts:export_library'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('accounts:login'), response.url)

    def test_export_and_import_roundtrip(self):
        self.client.force_login(self.user)
        export_resp = self.client.get(reverse('accounts:export_library'))
        self.assertEqual(export_resp.status_code, 200)
        self.assertEqual(export_resp['Content-Type'], 'application/json')

        data = json.loads(export_resp.content.decode('utf-8'))
        self.assertEqual(data['schema_version'], BACKUP_SCHEMA_VERSION)
        self.assertEqual(data['user']['username'], 'backup_user')
        self.assertEqual(data['user']['id'], str(self.user.pk))

        uploaded = SimpleUploadedFile(
            'backup.json',
            export_resp.content,
            content_type='application/json',
        )
        import_resp = self.client.post(
            reverse('accounts:import_library'),
            {'backup_file': uploaded},
            follow=True,
        )
        self.assertEqual(import_resp.status_code, 200)
        self.assertContains(import_resp, 'Backup restored:')

    def test_import_rejects_invalid_json_schema(self):
        self.client.force_login(self.user)
        bad_file = SimpleUploadedFile(
            'bad.json',
            b'{"schema_version": "unknown"}',
            content_type='application/json',
        )
        resp = self.client.post(
            reverse('accounts:import_library'),
            {'backup_file': bad_file},
            follow=True,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Import failed:')
