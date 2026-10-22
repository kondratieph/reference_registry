from django.contrib import admin
from django.db.models import OuterRef, Subquery
from django.utils import timezone

from reference_registry.models import (
    ReferenceBook,
    ReferenceBookItem,
    ReferenceBookVersion,
)


class ReferenceBookVersionInline(admin.TabularInline):
    model = ReferenceBookVersion
    fields = ('version', 'valid_from')
    extra = 1
    show_change_link = True


class ReferenceBookItemInline(admin.TabularInline):
    """Элементы на странице версии справочника."""

    model = ReferenceBookItem
    fields = ('code', 'value')
    extra = 1
    verbose_name_plural = 'Элементы справочника'


@admin.register(ReferenceBook)
class ReferenceBookAdmin(admin.ModelAdmin):
    list_display = (
        'identifier',
        'code',
        'name',
        'current_version',
        'current_version_start',
    )
    search_fields = ('code', 'name')
    empty_value_display = '—'
    inlines = (ReferenceBookVersionInline,)

    def get_queryset(self, request):
        # list_display выводит "текущую версию" и "дату её начала" — полей
        # с такими именами в модели нет, их надо вычислить.
        #
        # Текущая - это версия с максимальным valid_from, не позже сегодня.
        # Чтобы не дёргать БД на каждую строку списка (N+1), вычисляем её
        # Subquery прямо в SQL — один запрос на всю страницу.
        #
        # _current_version / _current_start — с префиксом _, чтобы не
        # конфликтовать с методами админки current_version / current_version_start

        current = ReferenceBookVersion.objects.filter(
            reference_book=OuterRef('pk'),
            valid_from__lte=timezone.localdate(),
        ).order_by('-valid_from')
        return super().get_queryset(request).annotate(
            _current_version=Subquery(current.values('version')[:1]),
            _current_start=Subquery(current.values('valid_from')[:1]),
        )

    # У поля id заголовок по умолчанию «ID», а в ТЗ колонка называется
    # «Идентификатор».
    @admin.display(description='Идентификатор', ordering='id')
    def identifier(self, obj):
        return obj.pk

    @admin.display(description='Текущая версия', ordering='_current_version')
    def current_version(self, obj):
        return obj._current_version

    @admin.display(
        description='Дата начала действия версии',
        ordering='_current_start',
    )
    def current_version_start(self, obj):
        return obj._current_start


@admin.register(ReferenceBookVersion)
class ReferenceBookVersionAdmin(admin.ModelAdmin):
    list_display = ('book_code', 'book_name', 'version', 'valid_from')
    list_select_related = ('reference_book',)
    list_filter = ('reference_book',)
    search_fields = (
        'version',
        'reference_book__code',
        'reference_book__name',
    )
    inlines = (ReferenceBookItemInline,)

    @admin.display(
        description='Код справочника',
        ordering='reference_book__code',
    )
    def book_code(self, obj):
        return obj.reference_book.code

    @admin.display(
        description='Наименование справочника',
        ordering='reference_book__name',
    )
    def book_name(self, obj):
        return obj.reference_book.name


@admin.register(ReferenceBookItem)
class ReferenceBookItemAdmin(admin.ModelAdmin):
    list_display = ('code', 'value', 'version')
    list_select_related = ('version__reference_book',)
    list_filter = ('version__reference_book',)
    search_fields = ('code', 'value')

    def formfield_for_foreignkey(
            self, db_field,
            request, **kwargs
    ):
        # __str__ версии обращается к справочнику: подгружаем его сразу,
        # иначе выпадающий список «справочник-версия» делает запрос на строку.
        if db_field.name == 'version':
            kwargs['queryset'] = (
                ReferenceBookVersion.objects.select_related('reference_book')
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
