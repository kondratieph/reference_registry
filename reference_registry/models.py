from django.db import models
from django.utils import timezone


class ReferenceBook(models.Model):
    """Справочник: контейнер кодов и их контекста."""

    code = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Код справочника',
    )
    name = models.CharField(
        max_length=300,
        verbose_name='Наименование'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )

    class Meta:
        verbose_name = 'Справочник'
        verbose_name_plural = 'Справочники'
        ordering = ['code']

    def __str__(self):
        return f'{self.code} — {self.name}'

    @classmethod
    def actual_books_on_date(cls, on_date):
        """Справочники, у которых есть действующая версия на указанную дату."""
        return cls.objects.filter(versions__valid_from__lte=on_date).distinct()

    def book_current_version(self, on_date=None):
        """Актуальная версия справочника на дату (объект или None)."""
        on_date = on_date or timezone.localdate()
        return self.versions.filter(
            valid_from__lte=on_date,
        ).order_by('-valid_from').first()


class ReferenceBookVersion(models.Model):
    """Версия справочника: снимок его состояния на определённую дату."""

    reference_book = models.ForeignKey(
        ReferenceBook,
        on_delete=models.CASCADE,
        related_name='versions',
        verbose_name='Справочник',
    )
    version = models.CharField(
        max_length=50,
        verbose_name='Версия'
    )
    valid_from = models.DateField(
        verbose_name='Дата начала действия версии',
    )

    class Meta:
        verbose_name = 'Версия справочника'
        verbose_name_plural = 'Версии справочников'
        ordering = ['reference_book', '-valid_from']
        constraints = [
            models.UniqueConstraint(
                fields=['reference_book', 'version'],
                name='uniq_book_version',
            ),
            models.UniqueConstraint(
                fields=['reference_book', 'valid_from'],
                name='uniq_book_valid_from',
            ),
        ]

    def __str__(self):
        return f'{self.reference_book.code} - {self.version}'


class ReferenceBookItem(models.Model):
    """Элемент справочника: пара 'код - значение' в конкретной версии."""

    version = models.ForeignKey(
        ReferenceBookVersion,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Версия',
    )
    code = models.CharField(
        max_length=100,
        verbose_name='Код элемента'
    )
    value = models.CharField(
        max_length=300,
        verbose_name='Значение элемента'
    )

    class Meta:
        verbose_name = 'Элемент справочника'
        verbose_name_plural = 'Элементы справочников'
        ordering = ['code']
        constraints = [
            models.UniqueConstraint(
                fields=['version', 'code'],
                name='uniq_version_item_code',
            ),
        ]

    def __str__(self):
        return f'{self.code}: {self.value}'
