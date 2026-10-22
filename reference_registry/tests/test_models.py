from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from reference_registry.models import ReferenceBook, ReferenceBookVersion


class ActualBooksOnDateTest(TestCase):
    def setUp(self):
        today = timezone.localdate()
        self.book_active = ReferenceBook.objects.create(code='A', name='A')
        ReferenceBookVersion.objects.create(
            reference_book=self.book_active,
            version='1.0',
            valid_from=today - timedelta(days=30),
        )
        self.book_future = ReferenceBook.objects.create(code='B', name='B')
        ReferenceBookVersion.objects.create(
            reference_book=self.book_future,
            version='1.0',
            valid_from=today + timedelta(days=30),
        )
        self.book_empty = ReferenceBook.objects.create(code='C', name='C')

    def test_includes_book_with_active_version(self):
        result = ReferenceBook.actual_books_on_date(timezone.localdate())
        self.assertIn(self.book_active, result)

    def test_excludes_book_with_future_version(self):
        result = ReferenceBook.actual_books_on_date(timezone.localdate())
        self.assertNotIn(self.book_future, result)

    def test_excludes_book_without_versions(self):
        result = ReferenceBook.actual_books_on_date(timezone.localdate())
        self.assertNotIn(self.book_empty, result)

    def test_excludes_book_before_any_version(self):
        past = timezone.localdate() - timedelta(days=60)
        result = ReferenceBook.actual_books_on_date(past)
        self.assertNotIn(self.book_active, result)

    def test_book_with_multiple_active_versions_returns_once(self):
        ReferenceBookVersion.objects.create(
            reference_book=self.book_active,
            version='2.0',
            valid_from=timezone.localdate() - timedelta(days=10),
        )
        result = ReferenceBook.actual_books_on_date(timezone.localdate())
        self.assertEqual(list(result).count(self.book_active), 1)


class BookCurrentVersionTest(TestCase):
    def setUp(self):
        today = timezone.localdate()
        self.book = ReferenceBook.objects.create(code='X', name='X')
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

    def test_returns_latest_not_after_date(self):
        today = timezone.localdate()
        self.assertEqual(self.book.book_current_version(today), self.v_new)
        self.assertEqual(
            self.book.book_current_version(today - timedelta(days=200)),
            self.v_old,
        )

    def test_returns_none_before_first_version(self):
        before = timezone.localdate() - timedelta(days=400)
        self.assertIsNone(self.book.book_current_version(before))

    def test_defaults_to_today(self):
        self.assertEqual(self.book.book_current_version(), self.v_new)