from django.core.cache import cache
from django.test import TestCase


class ViewTestClass(TestCase):
    def setUp(self) -> None:
        cache.clear()

    def test_error_page(self):
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'core/404.html')
