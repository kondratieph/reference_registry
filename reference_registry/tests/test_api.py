from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from reference_registry.models import (
    ReferenceBook,
    ReferenceBookItem,
    ReferenceBookVersion,
)

User = get_user_model()


class BaseAPITest(APITestCase):
    """Общие данные для тестов API. Аутентификация — в наследниках."""

    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='tester')

        today = timezone.localdate()

        self.book = ReferenceBook.objects.create(code='BOOK1', name='Book 1')
        self.v_old = ReferenceBookVersion.objects.create(
            reference_book=self.book,
            version='1.0',
            valid_from=today - timedelta(days=365),
        )
        self.v_new = ReferenceBookVersion.objects.create(
            reference_book=self.book,
            version='2.0',
            valid_from=today - timedelta(days=1),
        )
        ReferenceBookItem.objects.create(
            version=self.v_old, code='OLD', value='old value',
        )
        ReferenceBookItem.objects.create(
            version=self.v_new, code='NEW', value='new value',
        )

        self.book_future = ReferenceBook.objects.create(code='FUT', name='Future')
        ReferenceBookVersion.objects.create(
            reference_book=self.book_future,
            version='1.0',
            valid_from=today + timedelta(days=30),
        )

        self.book_empty = ReferenceBook.objects.create(code='EMPTY', name='Empty')


class AuthenticatedAPITest(BaseAPITest):
    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.user)


class AuthRequiredTest(BaseAPITest):
    """Без токена все три эндпоинта должны возвращать 401."""

    def test_list_requires_auth(self):
        response = self.client.get('/refbooks/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_elements_requires_auth(self):
        response = self.client.get(f'/refbooks/{self.book.pk}/elements/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_check_element_requires_auth(self):
        response = self.client.get(
            f'/refbooks/{self.book.pk}/check_element/',
            {'code': 'NEW', 'value': 'new value'},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class BookListTest(AuthenticatedAPITest):
    def test_returns_envelope(self):
        response = self.client.get('/refbooks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refbooks', response.data)
        codes = {b['code'] for b in response.data['refbooks']}
        self.assertEqual(codes, {'BOOK1', 'FUT', 'EMPTY'})

    def test_filters_by_date(self):
        response = self.client.get(
            '/refbooks/', {'date': timezone.localdate().isoformat()},
        )
        codes = {b['code'] for b in response.data['refbooks']}
        # BOOK1 актуален (v_new вчера); FUT в будущем; EMPTY без версий
        self.assertEqual(codes, {'BOOK1'})

    def test_date_before_any_version_returns_empty(self):
        past = (timezone.localdate() - timedelta(days=400)).isoformat()
        response = self.client.get('/refbooks/', {'date': past})
        self.assertEqual(response.data['refbooks'], [])

    def test_invalid_date_returns_400(self):
        response = self.client.get('/refbooks/', {'date': 'not-a-date'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('date', response.data)


class ElementsTest(AuthenticatedAPITest):
    def test_returns_current_version_envelope(self):
        response = self.client.get(f'/refbooks/{self.book.pk}/elements/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('elements', response.data)
        codes = {i['code'] for i in response.data['elements']}
        self.assertEqual(codes, {'NEW'})

    def test_explicit_version_returns_its_items(self):
        response = self.client.get(
            f'/refbooks/{self.book.pk}/elements/', {'version': '1.0'},
        )
        codes = {i['code'] for i in response.data['elements']}
        self.assertEqual(codes, {'OLD'})

    def test_unknown_version_returns_400(self):
        response = self.client.get(
            f'/refbooks/{self.book.pk}/elements/', {'version': '99'},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_book_not_found_returns_404(self):
        response = self.client.get('/refbooks/99999/elements/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_book_without_versions_returns_400(self):
        response = self.client.get(f'/refbooks/{self.book_empty.pk}/elements/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CheckElementTest(AuthenticatedAPITest):
    def test_present_in_current_version(self):
        response = self.client.get(
            f'/refbooks/{self.book.pk}/check_element/',
            {'code': 'NEW', 'value': 'new value'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'valid': True})

    def test_absent_value(self):
        response = self.client.get(
            f'/refbooks/{self.book.pk}/check_element/',
            {'code': 'NEW', 'value': 'wrong'},
        )
        self.assertEqual(response.data, {'valid': False})

    def test_present_in_explicit_version(self):
        response = self.client.get(
            f'/refbooks/{self.book.pk}/check_element/',
            {'code': 'OLD', 'value': 'old value', 'version': '1.0'},
        )
        self.assertEqual(response.data, {'valid': True})

    def test_absent_in_current_version_when_only_in_old(self):
        # OLD есть в 1.0, в актуальной 2.0 его нет
        response = self.client.get(
            f'/refbooks/{self.book.pk}/check_element/',
            {'code': 'OLD', 'value': 'old value'},
        )
        self.assertEqual(response.data, {'valid': False})

    def test_missing_params_returns_400(self):
        response = self.client.get(f'/refbooks/{self.book.pk}/check_element/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unknown_version_returns_400(self):
        response = self.client.get(
            f'/refbooks/{self.book.pk}/check_element/',
            {'code': 'NEW', 'value': 'new value', 'version': '99'},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_current_version_returns_400(self):
        response = self.client.get(
            f'/refbooks/{self.book_empty.pk}/check_element/',
            {'code': 'X', 'value': 'Y'},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class BookListIdTypeTest(AuthenticatedAPITest):
    def test_id_is_string_in_response(self):
        response = self.client.get('/refbooks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for book in response.data['refbooks']:
            self.assertIsInstance(book['id'], str)
