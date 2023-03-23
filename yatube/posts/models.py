from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import UniqueConstraint

User = get_user_model()
PUB_DATE_DESC: str = '-pub_date'
COMM_DATE_DESC: str = '-created'
POST_TEXT_LIMIT: int = 15


class Group(models.Model):
    """
    Group model is responsible for the group.
    """
    title = models.CharField('Заголовок', max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField('Описание')

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class Post(models.Model):
    """
    Post model is responsible for the post.
    """
    text = models.TextField(
        'Текст',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )

    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts_group',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост'
    )

    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = (PUB_DATE_DESC,)
        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return self.text[:POST_TEXT_LIMIT]


class CensoredWord(models.Model):
    """
    Prohibited words.
    """
    word = models.CharField('Запретное слово', max_length=50)

    class Meta:
        verbose_name = 'Слово'
        verbose_name_plural = 'Слова'

    def __str__(self):
        return self.word


class Comment(models.Model):
    """Comment model."""
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Публикация',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
    )
    text = models.TextField('Текст комментария', help_text='Введите текст',)
    created = models.DateTimeField(
        'Дата публикации комментария',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии',
        ordering = (COMM_DATE_DESC,)

    def __str__(self):
        return self.text[:POST_TEXT_LIMIT]


class Follow(models.Model):
    """Follow model."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки',

        constraints = [
            UniqueConstraint(
                name='unique_follow',
                fields=['user', 'author'],
            )
        ]

    def __str__(self):
        return f'{self.user.username} -> {self.author.username}'

    def clean(self):
        super().clean()

        if self.user == self.author:
            raise ValidationError('Нельзя подписаться на самого себя')
