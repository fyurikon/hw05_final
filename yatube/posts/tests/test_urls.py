from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest_client = Client()

        cls.user = User.objects.create(username='HasNoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.user_not_author = User.objects.create(username='NotAuthor')
        cls.authorized_not_author_client = Client()
        cls.authorized_not_author_client.force_login(cls.user_not_author)

        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
        )

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='some-slug',
            description='Тестовое описание',
        )

    def setUp(self) -> None:
        cache.clear()

    def test_home_url_exists_at_desired_location(self):
        """Page available for all users."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_desired_profile_url_exists_at_desired_location(self):
        """Page /profile/user/ available for all users."""
        response = self.guest_client.get('/profile/HasNoName/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_url_exists_at_desired_location(self):
        """Page posts/post_id/ available for all users."""
        response = self.guest_client.get(f'/posts/{self.post.id}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_url_exists_at_desired_location(self):
        """Page /group/slug/ availabale for all users."""
        response = self.guest_client.get('/group/some-slug/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_url_exists_at_desired_location(self):
        """Page /create/ available for authorized users only."""
        response_authorized = self.authorized_client.get('/create/')
        response_not_authorized = self.guest_client.get('/create/')

        self.assertEqual(response_authorized.status_code, HTTPStatus.OK)
        self.assertEqual(response_not_authorized.status_code,
                         HTTPStatus.FOUND)

    def test_post_edit_url_exists_at_desired_location(self):
        """Page /posts/post_id/edit/ available for post author only."""
        response_authorized = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            )
        )
        response_not_authorized = self.guest_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            )
        )
        response_not_author = self.authorized_not_author_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            )
        )

        self.assertEqual(
            response_authorized.status_code, HTTPStatus.OK
        )
        self.assertEqual(
            response_not_authorized.status_code, HTTPStatus.FOUND
        )
        self.assertEqual(
            response_not_author.status_code, HTTPStatus.FOUND
        )

    def test_404_url_exists_at_desired_location(self):
        """Page /404/ exists and available for all users."""
        response = self.guest_client.get('/unexisting_page/')

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """URL uses correct template."""
        templates_url_names = {
            '/group/some-slug/': 'posts/group_list.html',
            '/profile/HasNoName/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/': 'posts/index.html',
            '/unexisting_url/': 'core/404.html'
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
