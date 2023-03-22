from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import CensoredWord, Group, Post

User = get_user_model()
POST_TEXT_LIMIT: int = 15


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username='HasNoName')

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост длина которого больше 15 символов',
        )

    def test_post_model_has_correct_object_names(self):
        """Check that __str__ method is correct."""
        post = PostModelTest.post

        self.assertEqual(post.text[:POST_TEXT_LIMIT], post.__str__())

    def test_post_model_has_correct_help_text(self):
        """Check that models have correct help text."""
        post = PostModelTest.post
        help_text_text = post._meta.get_field('text').help_text

        self.assertEqual(help_text_text, 'Введите текст поста')

    def test_post_model_has_correct_verbose_names(self):
        """Check that models have correct verbose names."""
        post = PostModelTest.post

        verbose_text_text = post._meta.get_field('text').verbose_name
        verbose_text_group = post._meta.get_field('group').verbose_name
        verbose_text_author = post._meta.get_field('author').verbose_name
        verbose_pub_date = post._meta.get_field('pub_date').verbose_name
        verbose_post_name = post._meta.verbose_name
        verbose_post_name_plural = post._meta.verbose_name_plural

        self.assertEqual(verbose_text_text, 'Текст')
        self.assertEqual(verbose_text_group, 'Группа')
        self.assertEqual(verbose_text_author, 'Автор')
        self.assertEqual(verbose_pub_date, 'Дата публикации')
        self.assertEqual(verbose_post_name, 'Публикация')
        self.assertEqual(verbose_post_name_plural, 'Публикации')


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='some-slug',
            description='Тестовое описание',
        )

    def test_group_model_has_correct_object_names(self):
        """Check that __str__ method is correct."""
        group = GroupModelTest.group

        self.assertEqual(group.title, group.__str__())

    def test_group_model_has_correct_verbose_names(self):
        """Check that group model has correct verbose names."""
        group = GroupModelTest.group

        self.assertEqual(group._meta.verbose_name, 'Группа')
        self.assertEqual(group._meta.verbose_name_plural, 'Группы')


class CensoredWordModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.word = CensoredWord.objects.create(
            word='Охотник',
        )

    def test_censored_word_model_has_correct_object_names(self):
        """Check that __str__ method is correct."""
        word = CensoredWordModelTest.word

        self.assertEqual(word.word, word.__str__())

    def test_censored_word_model_has_correct_verbose_names(self):
        """Check that censored word model has correct verbose names."""
        word = CensoredWordModelTest.word

        self.assertEqual(word._meta.verbose_name, 'Слово')
        self.assertEqual(word._meta.verbose_name_plural, 'Слова')
