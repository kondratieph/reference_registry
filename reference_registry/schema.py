from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

# Параметры запросов

DATE_PARAM = openapi.Parameter(
    'date',
    openapi.IN_QUERY,
    description=(
        'Дата в формате YYYY-MM-DD. '
        'Возвращаются только справочники, актуальные на эту дату.'
    ),
    type=openapi.TYPE_STRING,
    format='date',
    required=False,
    x_example='2022-10-01',
)

VERSION_PARAM = openapi.Parameter(
    'version',
    openapi.IN_QUERY,
    description='Версия справочника (например, 1.0). Если не указана — актуальная на сегодня.',
    type=openapi.TYPE_STRING,
    required=False,
    x_example='1.0',
)

CODE_PARAM = openapi.Parameter(
    'code',
    openapi.IN_QUERY,
    description='Код элемента справочника.',
    type=openapi.TYPE_STRING,
    required=True,
    x_example='E001_001_AAA',
)

VALUE_PARAM = openapi.Parameter(
    'value',
    openapi.IN_QUERY,
    description='Значение элемента справочника.',
    type=openapi.TYPE_STRING,
    required=True,
    x_example='AAA',
)


# Схемы объектов

reference_book_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='Идентификатор справочника',
        ),
        'code': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='Код справочника',
        ),
        'name': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='Наименование справочника',
        ),
    },
)

# Envelope для GET /refbooks/: {"refbooks": [...]}
reference_book_list_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'refbooks': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=reference_book_schema,
            description='Список справочников',
        ),
    },
)

# Один элемент справочника.
reference_book_item_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'code': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='Код элемента',
        ),
        'value': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='Значение элемента',
        ),
    },
)

# Envelope для GET /refbooks/<id>/elements/: {"elements": [...]}
reference_book_item_list_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'elements': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=reference_book_item_schema,
            description='Список элементов справочника',
        ),
    },
)


BOOK_LIST_SCHEMA = swagger_auto_schema(
    tags=['Справочники'],
    operation_summary='Список справочников',
    operation_description=(
        'Возвращает список всех справочников. '
        'Если передан параметр `date`, возвращаются только справочники, '
        'у которых есть действующая версия на указанную дату.'
    ),
    manual_parameters=[DATE_PARAM],
    responses={
        200: openapi.Response(
            description='Список справочников',
            schema=reference_book_list_response,
            examples={
                'application/json': {
                    'refbooks': [
                        {'id': '1', 'code': 'MS1', 'name': 'Справочник 1'},
                        {'id': '2', 'code': 'ICD-10', 'name': 'МКБ-10'},
                    ],
                },
            },
        ),
    },
)

ELEMENTS_SCHEMA = swagger_auto_schema(
    tags=['Элементы справочника'],
    operation_summary='Элементы справочника',
    operation_description=(
        'Возвращает элементы заданного справочника. '
        'Если передан параметр `version`, возвращаются элементы указанной версии. '
        'Иначе — элементы актуальной версии на текущую дату.'
    ),
    manual_parameters=[VERSION_PARAM],
    responses={
        200: openapi.Response(
            description='Список элементов справочника',
            schema=reference_book_item_list_response,
            examples={
                'application/json': {
                    'elements': [
                        {'code': 'J00', 'value': 'Некоторые значения'},
                        {'code': 'J01', 'value': 'Другие значения'},
                    ],
                },
            },
        ),
    },
)

CHECK_ELEMENT_SCHEMA = swagger_auto_schema(
    tags=['Валидация элементов'],
    operation_summary='Проверка наличия элемента в справочнике',
    operation_description=(
        'Проверяет, присутствует ли элемент с указанным кодом и значением '
        'в заданной версии справочника. Если `version` не указана — '
        'проверка выполняется в актуальной версии на текущую дату. '
        'Ответ: `{"valid": true}` — элемент найден, `{"valid": false}` — не найден.'
    ),
    manual_parameters=[CODE_PARAM, VALUE_PARAM, VERSION_PARAM],
    responses={
        200: openapi.Response(
            description='Результат проверки',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'valid': openapi.Schema(
                        type=openapi.TYPE_BOOLEAN,
                        description=(
                            'true — элемент найден, '
                            'false — не найден.'
                        ),
                    ),
                },
            ),
            examples={
                'application/json': {'valid': True},
            },
        ),
    },
)
