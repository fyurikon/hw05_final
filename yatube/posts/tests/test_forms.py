import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post

User = get_user_model()
ONE_POST: int = 1
ONE_COMMENT: int = 1
IMG_FOLDER = Post.image.field.upload_to
TEST_GIF = (
    b"\x47\x49\x46\x38\x39\x61\x02\x00"
    b"\x01\x00\x80\x00\x00\x00\x00\x00"
    b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
    b"\x00\x00\x00\x2C\x00\x00\x00\x00"
    b"\x02\x00\x01\x00\x00\x02\x02\x0C"
    b"\x0A\x00\x3B"
)

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormCreateEditTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest_client = Client()

        cls.user = User.objects.create(username='HasNoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.user_not_author = User.objects.create(username='NotAuthor')
        cls.authorized_client_not_author = Client()
        cls.authorized_client_not_author.force_login(cls.user_not_author)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='some-slug',
            description='Тестовое описание',
        )

    def setUp(self) -> None:
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_post_create_authorized(self):
        """New post is created and added to database."""
        uploaded_img = SimpleUploadedFile(
            name='test_gif.gif',
            content=TEST_GIF,
            content_type='image/gif')

        post_content = {
            'text': 'Особый пост',
            'group': self.group.pk,
            'image': uploaded_img,
        }

        posts_nbr_before_creation = Post.objects.count()

        self.authorized_client.post(
            reverse('posts:post_create'),
            data=post_content,
        )

        posts_nbr_after_creation = Post.objects.count()
        post = Post.objects.select_related('group', 'author').get()

        self.assertEqual(post_content['text'], post.text)
        self.assertEqual(post_content['group'], post.group.pk)
        self.assertEqual(post.image, IMG_FOLDER + uploaded_img.name)
        self.assertEqual(self.user, post.author)
        self.assertEqual(
            posts_nbr_before_creation + ONE_POST,
            posts_nbr_after_creation
        )

    def test_post_create_authorized_without_group(self):
        """New post is created and added to database."""
        post_content = {
            'text': 'Пост без группы'
        }

        posts_nbr_before_creation = Post.objects.count()

        self.authorized_client.post(
            reverse('posts:post_create'),
            data=post_content,
        )

        posts_nbr_after_creation = Post.objects.count()
        first_post = Post.objects.select_related('group', 'author').get()

        self.assertEqual(post_content['text'], first_post.text)
        self.assertEqual(first_post.group, None)
        self.assertEqual(self.user, first_post.author)
        self.assertEqual(
            posts_nbr_before_creation + ONE_POST,
            posts_nbr_after_creation
        )

    def test_post_create_not_authorized(self):
        """New post is not created by guest and not added to database."""
        post_content = {
            'text': 'Особый пост',
            'group': self.group.pk
        }

        posts_nbr_before_creation = Post.objects.count()

        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=post_content,
        )

        posts_nbr_after_creation = Post.objects.count()

        self.assertEqual(
            posts_nbr_before_creation,
            posts_nbr_after_creation
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.FOUND
        )

    def test_post_edit_authorized(self):
        """Old post is successfully edited by authorized user."""
        created_post = Post.objects.create(
            text='Особый пост',
            author=self.user,
            group=self.group
        )

        post_edited_content = {
            'text': 'Особый пост отредактирован',
            'group': self.group.pk
        }

        self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={
                    'post_id': created_post.id
                }
            ),
            data=post_edited_content
        )

        edited_post = Post.objects.select_related('group', 'author').get()

        self.assertEqual(edited_post.pub_date, created_post.pub_date)
        self.assertEqual(edited_post.author, created_post.author)
        self.assertEqual(edited_post.text, post_edited_content['text'])
        self.assertEqual(edited_post.group.pk, post_edited_content['group'])

    def test_post_edit_not_authorized(self):
        """Old post is not edited by guest."""
        created_post = Post.objects.create(
            text='Особый пост',
            author=self.user,
            group=self.group
        )

        post_edited_content = {
            'text': 'Особый пост отредактирован',
            'group': self.group.pk
        }

        response = self.guest_client.post(
            reverse(
                'posts:post_edit',
                kwargs={
                    'post_id': created_post.id
                }
            ),
            data=post_edited_content
        )

        edited_post = Post.objects.select_related('group', 'author').get()

        self.assertEqual(edited_post.pub_date, created_post.pub_date)
        self.assertEqual(edited_post.author, created_post.author)
        self.assertEqual(edited_post.text, created_post.text)
        self.assertEqual(edited_post.group.pk, created_post.group.pk)
        self.assertEqual(
            response.status_code,
            HTTPStatus.FOUND
        )

    def test_post_edit_authorized_not_author(self):
        """Old post is not edited by authorized user not author."""
        created_post = Post.objects.create(
            text='Особый пост',
            author=self.user,
            group=self.group
        )

        post_edited_content = {
            'text': 'Особый пост отредактирован',
            'group': self.group.pk
        }

        response = self.authorized_client_not_author.post(
            reverse(
                'posts:post_edit',
                kwargs={
                    'post_id': created_post.id
                }
            ),
            data=post_edited_content
        )

        edited_post = Post.objects.select_related('group', 'author').get()

        self.assertEqual(edited_post.pub_date, created_post.pub_date)
        self.assertEqual(edited_post.author, created_post.author)
        self.assertEqual(edited_post.text, created_post.text)
        self.assertEqual(edited_post.group.pk, created_post.group.pk)
        self.assertEqual(
            response.status_code,
            HTTPStatus.FOUND
        )

    def test_add_comment_authorized(self):
        special_post = Post.objects.create(
            text='Особый пост для всяческих тестовых нужд.',
            author=self.user_not_author,
            group=self.group
        )

        comment_content = {
            'text': 'Комментарий который точно пройдёт валидацию'
        }

        comments_nbr_before_creation = Comment.objects.count()

        self.authorized_client.post(
            reverse(
                'posts:add_comment', args=[special_post.id]
            ),
            comment_content
        )

        comments_nbr_after_creation = Comment.objects.count()
        comment = Comment.objects.first()

        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': special_post.id}
            )
        )

        self.assertEqual(
            comments_nbr_before_creation + ONE_COMMENT,
            comments_nbr_after_creation
        )
        self.assertEqual(comment.text, comment_content['text'])
        self.assertEqual(
            comment.author.username,
            self.user.username
        )
        self.assertEqual(comment.post, special_post)
        self.assertEqual(response.context['comments'][0], comment)

    def test_add_comment_not_authorized(self):
        special_post = Post.objects.create(
            text='Особый пост для всяческих тестовых нужд.',
            author=self.user_not_author,
            group=self.group
        )

        comment_content = {
            'text': 'Комментарий который точно пройдёт валидацию'
        }

        comments_nbr_before_creation = Comment.objects.count()

        self.guest_client.post(
            reverse(
                'posts:add_comment', args=[special_post.id]
            ),
            comment_content
        )

        comments_nbr_after_creation = Comment.objects.count()

        self.assertEqual(
            comments_nbr_before_creation,
            comments_nbr_after_creation
        )
