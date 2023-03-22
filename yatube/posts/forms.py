from typing import Tuple

from django import forms

from .models import CensoredWord, Comment, Post
from .utils import bad_language_validation

SIMILARITY_THRESHOLD: float = 0.9


class PostForm(forms.ModelForm):
    class Meta:
        model = Post

        fields = ('text', 'group', 'image')

    def clean_text(self):
        text: str = self.cleaned_data['text']
        stop_words = CensoredWord.objects.values_list('word', flat=True)

        data: Tuple[str, bool] = bad_language_validation(
            text,
            stop_words,
            SIMILARITY_THRESHOLD
        )

        text = data[0]
        validation_error = data[1]

        if validation_error:
            raise forms.ValidationError(
                ('Пожалуйста, исправьте слова, что '
                 'отмечены звёздочками: %(value)s'),
                code='invalid',
                params={'value': text})

        return text


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)

    def clean_text(self):
        text: str = self.cleaned_data['text']
        stop_words = CensoredWord.objects.values_list('word', flat=True)

        data: Tuple[str, bool] = bad_language_validation(
            text,
            stop_words,
            SIMILARITY_THRESHOLD
        )

        text = data[0]
        validation_error = data[1]

        if validation_error:
            raise forms.ValidationError(
                ('Пожалуйста, исправьте слова, что '
                 'отмечены звёздочками: %(value)s'),
                code='invalid',
                params={'value': text})

        return text
