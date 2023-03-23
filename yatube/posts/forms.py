from .base_form import BaseForm
from .models import Comment, Post


class PostForm(BaseForm):
    class Meta:
        model = Post

        fields = ('text', 'group', 'image')


class CommentForm(BaseForm):
    class Meta:
        model = Comment
        fields = ("text",)
