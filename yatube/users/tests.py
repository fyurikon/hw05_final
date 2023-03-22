from http import HTTPStatus

from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()
ONE: int = 1


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest_client = Client()

        cls.user = User.objects.create(username='HasNoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def setUp(self) -> None:
        cache.clear()

    def test_user_guest_urls_exists_at_desired_location(self):
        """User pages are available."""
        templates_pages_names = {
            reverse('users:signup'): HTTPStatus.OK,
            reverse('users:login'): HTTPStatus.OK,
            reverse('users:logout'): HTTPStatus.OK,
            reverse('users:password_reset'): HTTPStatus.OK,
            reverse('users:password_reset_done'): HTTPStatus.OK,
            reverse('users:password_reset_complete'): HTTPStatus.OK,
            reverse(
                'users:password_reset_confirm', args=['uid64', 'token']
            ): HTTPStatus.OK,
        }

        for page, status_code in templates_pages_names.items():
            with self.subTest(status_code=status_code):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, status_code)

    def test_user_authorized_urls_exists_at_desired_location(self):
        """Authorized user pages are available."""
        templates_pages_names = {
            reverse('users:password_change_done'): HTTPStatus.OK,
            reverse('users:password_change'): HTTPStatus.OK,
        }

        for page, status_code in templates_pages_names.items():
            with self.subTest(status_code=status_code):
                response = self.authorized_client.get(page)
                self.assertEqual(response.status_code, status_code)

    def test_user_pages_use_correct_template(self):
        """User pages use correct template."""
        templates_pages_names = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
            reverse('users:logout'): 'users/logged_out.html',
            reverse('users:password_reset'): 'users/password_reset_form.html',
            reverse('users:password_reset_done'):
                'users/password_reset_done.html',
            reverse('users:password_reset_complete'):
                'users/password_reset_complete.html',
            reverse(
                'users:password_reset_confirm', args=['uid64', 'token']
            ): 'users/password_reset_confirm.html',
        }

        for page, template in templates_pages_names.items():
            with self.subTest(template=template):
                response = self.guest_client.get(page)
                self.assertTemplateUsed(response, template)

    def test_user_authorized_pages_use_correct_template(self):
        """User pages use correct template."""
        templates_pages_names = {
            reverse('users:password_change_done'):
                'users/password_change_done.html',
            reverse('users:password_change'):
                'users/password_change_form.html',
        }

        for page, template in templates_pages_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(page)
                self.assertTemplateUsed(response, template)

    def test_signup_page_show_correct_context(self):
        """Signup page with correct context."""
        response = self.guest_client.get(reverse('users:signup'))

        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
            'password1': forms.fields.CharField,
            'password2': forms.fields.CharField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_user_signup(self):
        """New user is created and added to database."""
        user_content = {
            'username': 'Rick',
            'password1': '8Rick18!#',
            'password2': '8Rick18!#'
        }

        user_nbr_before_creation = User.objects.count()

        response = self.guest_client.post(
            reverse('users:signup'),
            data=user_content,
        )

        user_nbr_after_creation = User.objects.count()

        self.assertEqual(
            user_nbr_before_creation + ONE,
            user_nbr_after_creation
        )
        self.assertTrue(User.objects.filter(username='Rick').exists())
        self.assertRedirects(response, reverse('posts:index'))
