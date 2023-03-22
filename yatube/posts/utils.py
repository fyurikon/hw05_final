from difflib import SequenceMatcher
from typing import List, Tuple

import nltk
import pymorphy2
from django.core.paginator import Paginator
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize

nltk.download('punkt')


def get_paginator(request, posts, posts_per_page):
    """Get page_obj via paginator."""
    paginator = Paginator(posts, posts_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return page_obj


def join_punctuation(seq: List[str], characters: str = '.,;?!') -> str:
    """Combine words and characters into string."""
    characters = set(characters)
    seq = iter(seq)
    current = next(seq)

    for nxt in seq:
        if nxt in characters:
            current += nxt
        else:
            yield current
            current = nxt

    yield current


def lemmatize_words(tokenized_words: List[str]) -> List[str]:
    """Lemmatize words."""
    morph = pymorphy2.MorphAnalyzer()
    result = [morph.parse(word)[0].normal_form for word in tokenized_words]

    return result


def stemmatize_words(tokenized_words: List[str]) -> List[str]:
    """Stemmatize words."""
    snowball = SnowballStemmer("russian")
    result = [snowball.stem(word) for word in tokenized_words]

    return result


def bad_language_validation(text: str, stop_words: List[str],
                            similarity_threshold: float) -> Tuple[str, bool]:
    """Check if text contains bad words and replace it with asterisks."""
    bad_words_idx: int = []
    validation_error: bool = False
    tokenized_words: List[str] = word_tokenize(text)

    lemmatized_words: List[str] = lemmatize_words(tokenized_words)
    lemmatized_stop_words: List[str] = lemmatize_words(stop_words)

    stemmed_stop_words: List[str] = stemmatize_words(lemmatized_stop_words)
    stemmed_words: List[str] = stemmatize_words(lemmatized_words)

    for i in range(len(stemmed_words)):
        if stemmed_words[i] in stemmed_stop_words:
            bad_words_idx.append(i)
            validation_error = True
            continue

        for stop_word in stemmed_stop_words:
            s = SequenceMatcher(None, stop_word, stemmed_words[i])
            if s.quick_ratio() > similarity_threshold:
                bad_words_idx.append(i)
                validation_error = True

    bad_words_idx = set(bad_words_idx)

    for i in bad_words_idx:
        tokenized_words[i] = '*' * len(tokenized_words[i])

    result: str = ' '.join(join_punctuation(tokenized_words))

    return result, validation_error
