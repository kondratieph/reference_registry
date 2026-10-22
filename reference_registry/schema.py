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
    description=(
        'Версия справочника (например, 1.0). '
        'Если не указана — актуальная на сегодня.'
    ),
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


# Схемы успешных ответов

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

check_element_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'valid': openapi.Schema(
            type=openapi.TYPE_BOOLEAN,
            description='true — элемент найден, false — не найден.',
        ),
    },
)


# Схемы ошибок

DETAIL_ERROR_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'detail': openapi.Schema(type=openapi.TYPE_STRING),
    },
)

NOT_AUTHENTICATED_RESPONSE = openapi.Response(
    description='Не аутентифицирован (отсутствует или неверный токен)',
    schema=DETAIL_ERROR_SCHEMA,
    examples={
        'application/json': {'detail': 'Учетные данные не были предоставлены.'},
    },
)

NOT_FOUND_RESPONSE = openapi.Response(
    description='Справочник с указанным id не найден',
    schema=DETAIL_ERROR_SCHEMA,
    examples={
        'application/json': {'detail': 'Не найдено.'},
    },
)

BOOK_LIST_400_RESPONSE = openapi.Response(
    description='Некорректный параметр date',
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={'date': openapi.Schema(type=openapi.TYPE_STRING)},
    ),
    examples={
        'application/json': {'date': 'Ожидается формат YYYY-MM-DD.'},
    },
)

ELEMENTS_400_RESPONSE = openapi.Response(
    description=(
        'Ошибка параметра version. Возможные случаи:\n'
        '- Неизвестная версия: `{"version": "Версия \\"99\\" не найдена."}`\n'
        '- Нет актуальной версии: '
        '`{"version": "У справочника нет действующей версии."}`'
    ),
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={'version': openapi.Schema(type=openapi.TYPE_STRING)},
    ),
    examples={
        'application/json': {'version': 'Версия "99" не найдена.'},
    },
)

CHECK_ELEMENT_400_RESPONSE = openapi.Response(
    description=(
        'Ошибка валидации параметров. Возможные случаи:\n'
        '- Отсутствует code или value: '
        '`{"detail": "Параметры code и value обязательны."}`\n'
        '- Неизвестная версия: `{"version": "Версия \\"99\\" не найдена."}`\n'
        '- Нет актуальной версии: '
        '`{"version": "У справочника нет действующей версии."}`'
    ),
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'detail': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='При отсутствии code или value',
            ),
            'version': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='При проблеме с версией',
            ),
        },
    ),
    examples={
        'application/json': {'detail': 'Параметры code и value обязательны.'},
    },
)


# Декораторы ручек

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
        400: BOOK_LIST_400_RESPONSE,
        401: NOT_AUTHENTICATED_RESPONSE,
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
                        {'code': 'J00', 'value': 'Острый назофарингит'},
                        {'code': 'J01', 'value': 'Острый синусит'},
                    ],
                },
            },
        ),
        400: ELEMENTS_400_RESPONSE,
        401: NOT_AUTHENTICATED_RESPONSE,
        404: NOT_FOUND_RESPONSE,
    },
)

CHECK_ELEMENT_SCHEMA = swagger_auto_schema(
    tags=['Валидация элементов'],
    operation_summary='Проверка наличия элемента в справочнике',
    operation_description=(
        'Проверяет, присутствует ли элемент с указанным кодом и значением '
        'в заданной версии справочника. Если `version` не указана — '
        'проверка выполняется в актуальной версии на текущую дату. '
        'Ответ: `{"valid": true}` — элемент найден, '
        '`{"valid": false}` — не найден.'
    ),
    manual_parameters=[CODE_PARAM, VALUE_PARAM, VERSION_PARAM],
    responses={
        200: openapi.Response(
            description='Результат проверки',
            schema=check_element_response,
            examples={
                'application/json': {'valid': True},
            },
        ),
        400: CHECK_ELEMENT_400_RESPONSE,
        401: NOT_AUTHENTICATED_RESPONSE,
        404: NOT_FOUND_RESPONSE,
    },
)