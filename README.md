# Reference Registry API

Сервис терминологии для обмена электронными документами. Хранит справочники
кодов и их контекст: справочники → версии → элементы. Предоставляет REST API
для получения справочников, их элементов и валидации элементов по коду и значению.

## Стек

- Python 3.13
- Django 6.1
- Django REST Framework 3.18
- drf-yasg (Swagger UI)
- SQLite (по умолчанию)

## Быстрый старт

```bash
# 1. Клонировать репозиторий
git clone <repo-url>
cd tz_reference_registry

# 2. Создать и активировать виртуальное окружение
python3 -m venv venv
source venv/bin/activate          # Linux / macOS
# venv\Scripts\activate            # Windows

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Применить миграции
python manage.py migrate

# 5. Создать администратора (для входа в /admin/)
python manage.py createsuperuser

# 6. Запустить сервер разработки
python manage.py runserver
```

Сервер будет доступен по адресу `http://127.0.0.1:8000/`.

## Наполнение данными

Через админку: `http://127.0.0.1:8000/admin/` — раздел «Справочники».
Создайте справочник, затем его версии (на странице справочника), затем
элементы (на странице версии).

## Аутентификация

Все эндпоинты API требуют токен (`TokenAuthentication`).

### Получить токен

```bash
curl -X POST http://127.0.0.1:8000/api-token-auth/ \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "ваш_пароль"}'
```

Ответ:

```json
{"token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"}
```

**Альтернатива** — создать токен из консоли:

```bash
python manage.py drf_create_token admin
```

### Использовать токен

Передавайте его в заголовке `Authorization`:

```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

## Эндпоинты

### 1. Список справочников

```
GET /refbooks/ [?date=YYYY-MM-DD]
```

Без `date` — все справочники. С `date` — только те, у которых есть
действующая версия на указанную дату.

**Пример:**

```bash
curl -H "Authorization: Token <токен>" \
     "http://127.0.0.1:8000/refbooks/"
```

```json
{
  "refbooks": [
    {"id": "1", "code": "MS1", "name": "Справочник 1"},
    {"id": "2", "code": "ICD-10", "name": "МКБ-10"}
  ]
}
```

### 2. Элементы справочника

```
GET /refbooks/<id>/elements/ [?version=<version>]
```

Без `version` — элементы актуальной версии на сегодня.
С `version` — элементы указанной версии.

**Пример:**

```bash
curl -H "Authorization: Token <токен>" \
     "http://127.0.0.1:8000/refbooks/1/elements/"
```

```json
{
  "elements": [
    {"code": "J00", "value": "Острый назофарингит"},
    {"code": "J01", "value": "Острый синусит"}
  ]
}
```

### 3. Валидация элемента

```
GET /refbooks/<id>/check_element/?code=<code>&value=<value> [&version=<version>]
```

Проверяет, есть ли элемент с указанным кодом и значением в версии справочника.
Если `version` не указана — проверка в актуальной версии на сегодня.

**Пример:**

```bash
curl -H "Authorization: Token <токен>" \
     "http://127.0.0.1:8000/refbooks/1/check_element/?code=J00&value=Острый+назофарингит"
```

```json
{"valid": true}
```

## Swagger UI

Документация API с примерами запросов и ответов:

```
http://127.0.0.1:8000/swagger/
```

**Авторизация в Swagger UI:** нажмите кнопку **Authorize** в правом верхнем
углу и введите токен в формате `Token <ваш_токен>` — с префиксом `Token`
и пробелом. Без префикса запросы вернут `401`.

## Тесты

```bash
python manage.py test reference_registry
```

Покрыто: модели (правило «актуальной версии», границы дат, уникальность),
API (все три эндпоинта, успешные и ошибочные сценарии), аутентификация,
генерация OpenAPI-схемы.

## Структура проекта

```
tz_reference_registry/
├── manage.py
├── requirements.txt
├── project/                 # настройки Django
│   ├── settings.py
│   └── urls.py
└── reference_registry/      # приложение «Сервис терминологии»
    ├── models.py            # ReferenceBook, ReferenceBookVersion, ReferenceBookItem
    ├── serializers.py       # DRF-сериализаторы
    ├── views.py             # API-вьюхи
    ├── schema.py            # OpenAPI-схемы для Swagger
    ├── admin.py             # настройка админки
    ├── urls.py              # маршруты приложения
    └── tests/               # тесты
        ├── test_models.py
        └── test_api.py
```

## Основные сценарии

### «Актуальная версия на дату»

Версия с максимальной `valid_from`, которая **не позже** указанной даты.
Реализовано в `ReferenceBook.book_current_version()` и
`ReferenceBook.actual_books_on_date()`.

### Границы дат

`valid_from <= date` — версия включается в день начала действия.
Если `date` на один день раньше `valid_from` — версия не действует.