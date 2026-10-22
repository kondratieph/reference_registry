from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from reference_registry.models import ReferenceBook, ReferenceBookItem
from reference_registry.schema import (
    BOOK_LIST_SCHEMA,
    CHECK_ELEMENT_SCHEMA,
    ELEMENTS_SCHEMA,
)
from reference_registry.serializers import (
    ReferenceBookItemSerializer,
    ReferenceBookSerializer,
)

def resolve_version(book, version_param=None):
    """Поиск текущей версии справочника."""
    if version_param:
        version = book.versions.filter(version=version_param).first()
        if version is None:
            raise ValidationError({'version': f'Версия "{version_param}" не найдена.'})
        return version
    version = book.book_current_version()
    if version is None:
        raise ValidationError({'version': 'У справочника нет действующей версии.'})
    return version

class ReferenceBookListView(generics.ListAPIView):
    """GET /refbooks/..."""
    serializer_class = ReferenceBookSerializer
    queryset = ReferenceBook.objects.all()

    @BOOK_LIST_SCHEMA
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        date_param = self.request.query_params.get('date')

        if date_param:
            try:
                on_date = parse_date(date_param)
            except ValueError:
                on_date = None

            if on_date is None:
                raise ValidationError({'date': 'Неверный формат даты!'})

            qs = ReferenceBook.actual_books_on_date(on_date)
        return qs

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        return Response({'refbooks': response.data})

class ElementsView(generics.ListAPIView):
    """GET /refbooks/<id>/elements... """
    serializer_class = ReferenceBookItemSerializer

    @ELEMENTS_SCHEMA
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ReferenceBookItem.objects.none()
        book = get_object_or_404(ReferenceBook, pk=self.kwargs['id'])
        version = resolve_version(
            book, self.request.query_params.get('version')
        )
        return version.items.all()

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({'elements': response.data})

class CheckElementView(APIView):
    """GET /refbooks/<id>/check_element... """

    @CHECK_ELEMENT_SCHEMA
    def get(self, request, id):
        book = get_object_or_404(ReferenceBook, pk=id)
        code = request.query_params.get('code')
        value = request.query_params.get('value')

        if not code or not value:
            raise ValidationError(
                {'detail': 'Параметры code и value обязательны.'}
            )
        version = resolve_version(
            book, request.query_params.get('version')
        )
        is_valid = version.items.filter(code=code, value=value).exists()
        return Response({'valid': is_valid})
