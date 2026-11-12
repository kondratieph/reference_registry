# Reference Registry API

A terminology service for exchanging electronic documents. Stores reference books of codes and their context: reference books → versions → elements. Provides a REST API for retrieving reference books, their elements, and validating elements by code and value.

![Tests](https://github.com/kondratieph/reference_registry/actions/workflows/tests.yaml/badge.svg)


## Stack

- Python 3.13
- Django 6.1
- Django REST Framework 3.18
- drf-yasg (Swagger UI)
- PostgreSQL (via Docker Compose)
- pytest + pytest-django
- Docker + Docker Compose
- GitHub Actions (CI)

## Quick start (Docker)

```bash
# 1. Clone the repository
git clone <repo-url>
cd reference_registry

# 2. Build and start the containers
docker compose up --build
```

The application will be available at `http://127.0.0.1:8000/`.

The container entrypoint automatically applies migrations, creates the admin user and generates an API token.

## Quick start (without Docker)

```bash
# 1. Clone the repository
git clone <repo-url>
cd reference_registry

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate          # Linux / macOS
# venv\Scripts\activate            # Windows

# 3. Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt

# 4. Apply migrations (requires a running PostgreSQL)
python manage.py migrate

# 5. Create an admin user (for /admin/ login)
python manage.py createsuperuser

# 6. Start the development server
python manage.py runserver
```

## Filling with data

Via the admin panel: `http://127.0.0.1:8000/admin/` — "Reference books" section.
Create a reference book, then its versions (on the book's page), then elements
(on the version's page).

## Authentication

All API endpoints require a token (`TokenAuthentication`).

### Getting a token

When running via Docker, a token for the admin user is created automatically and
printed to the logs:

```bash
docker compose logs reference-registry-service | grep -i token
```

**Alternative 1** — create a token from the console:

```bash
docker compose exec reference-registry-service python manage.py drf_create_token admin
```

**Alternative 2** — via the admin panel: `/admin/` → **Auth Token → Tokens**.

### Using the token

Pass it in the `Authorization` header:

```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

## Endpoints

### 1. List of reference books

```
GET /refbooks/ [?date=YYYY-MM-DD]
```

Without `date` — all reference books. With `date` — only those that have a
version valid on the specified date.

**Example:**

```bash
curl -H "Authorization: Token <token>" \
     "http://127.0.0.1:8000/refbooks/"
```

```json
{
  "refbooks": [
    {"id": "1", "code": "MS1", "name": "Reference book 1"},
    {"id": "2", "code": "ICD-10", "name": "ICD-10"}
  ]
}
```

### 2. Elements of a reference book

```
GET /refbooks/<id>/elements/ [?version=<version>]
```

Without `version` — elements of the actual version as of today.
With `version` — elements of the specified version.

**Example:**

```bash
curl -H "Authorization: Token <token>" \
     "http://127.0.0.1:8000/refbooks/1/elements/"
```

```json
{
  "elements": [
    {"code": "J00", "value": "Acute nasopharyngitis"},
    {"code": "J01", "value": "Acute sinusitis"}
  ]
}
```

### 3. Element validation

```
GET /refbooks/<id>/check_element/?code=<code>&value=<value> [&version=<version>]
```

Checks whether an element with the given code and value exists in the version of
the reference book. If `version` is not specified, checks the actual version as
of today.

**Example:**

```bash
curl -H "Authorization: Token <token>" \
     "http://127.0.0.1:8000/refbooks/1/check_element/?code=J00&value=Acute+nasopharyngitis"
```

```json
{"valid": true}
```

## Swagger UI

API documentation with request and response examples:

```
http://127.0.0.1:8000/swagger/
```

**Authorization in Swagger UI:** click **Authorize** in the top right corner and
enter the token as `Token <your_token>` — with the `Token` prefix and a space.
Without the prefix, requests will return `401`.

## Tests

```bash
# Via Docker
docker compose exec reference-registry-service pytest

# Locally (requires a running PostgreSQL)
pytest
```

Covered: models ("actual version" rule, date boundaries, uniqueness),
API (all three endpoints, success and error scenarios), authentication,
OpenAPI schema generation.

## Project structure

```
reference_registry/
├── manage.py
├── requirements.txt
├── requirements-test.txt
├── Dockerfile
├── docker-compose.yaml
├── entrypoint_local.sh
├── pytest.ini
├── .github/
│   └── workflows/
│       └── tests.yaml
├── project/                 # Django settings
│   ├── settings.py
│   └── urls.py
└── reference_registry/      # "Terminology Service" app
    ├── models.py            # ReferenceBook, ReferenceBookVersion, ReferenceBookItem
    ├── serializers.py       # DRF serializers
    ├── views.py             # API views
    ├── schema.py            # OpenAPI schemas for Swagger
    ├── admin.py             # Admin configuration
    ├── urls.py              # App routes
    └── tests/               # Tests
        ├── test_models.py
        └── test_api.py
```

## Key scenarios

### "Actual version as of a date"

The version with the maximum `valid_from` that is **not later than** the
specified date. Implemented in `ReferenceBook.book_current_version()` and
`ReferenceBook.actual_books_on_date()`.

### Date boundaries

`valid_from <= date` — the version is included on its start date.
If `date` is one day earlier than `valid_from` — the version is not valid.

## Notes

- **`DEBUG = True`** is left as default for convenience of review
  (`/admin/`, debug pages, static files).

---

<details>
<summary>Русская версия</summary>

# Reference Registry API

Сервис терминологии для обмена электронными документами. Хранит справочники
кодов и их контекст: справочники → версии → элементы. Предоставляет REST API
для получения справочников, их элементов и валидации элементов по коду и значению.

## Стек

- Python 3.13
- Django 6.1
- Django REST Framework 3.18
- drf-yasg (Swagger UI)
- PostgreSQL (через Docker Compose)
- pytest + pytest-django
- Docker + Docker Compose
- GitHub Actions (CI)

## Быстрый старт (Docker)

```bash
# 1. Клонировать репозиторий
git clone <repo-url>
cd reference_registry

# 2. Собрать и запустить контейнеры
docker compose up --build
```

Приложение будет доступно по адресу `http://127.0.0.1:8000/`.

Entrypoint контейнера автоматически применяет миграции, создаёт администратора
и генерирует API-токен.

## Быстрый старт (без Docker)

```bash
# 1. Клонировать репозиторий
git clone <repo-url>
cd reference_registry

# 2. Создать и активировать виртуальное окружение
python3 -m venv venv
source venv/bin/activate          # Linux / macOS
# venv\Scripts\activate            # Windows

# 3. Установить зависимости
pip install -r requirements.txt
pip install -r requirements-test.txt

# 4. Применить миграции (требуется запущенный PostgreSQL)
python manage.py migrate

# 5. Создать администратора (для входа в /admin/)
python manage.py createsuperuser

# 6. Запустить сервер разработки
python manage.py runserver
```

## Наполнение данными

Через админку: `http://127.0.0.1:8000/admin/` — раздел «Справочники».
Создайте справочник, затем его версии (на странице справочника), затем
элементы (на странице версии).

## Аутентификация

Все эндпоинты API требуют токен (`TokenAuthentication`).

### Получить токен

При запуске через Docker токен для администратора создаётся автоматически и
печатается в логи:

```bash
docker compose logs reference-registry-service | grep -i token
```

**Альтернатива 1** — создать токен из консоли:

```bash
docker compose exec reference-registry-service python manage.py drf_create_token admin
```

**Альтернатива 2** — через админку: `/admin/` → **Auth Token → Tokens**.

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
# Через Docker
docker compose exec reference-registry-service pytest

# Локально (требуется запущенный PostgreSQL)
pytest
```

Покрыто: модели (правило «актуальной версии», границы дат, уникальность),
API (все три эндпоинта, успешные и ошибочные сценарии), аутентификация,
генерация OpenAPI-схемы.

## Структура проекта

```
reference_registry/
├── manage.py
├── requirements.txt
├── requirements-test.txt
├── Dockerfile
├── docker-compose.yaml
├── entrypoint_local.sh
├── pytest.ini
├── .github/
│   └── workflows/
│       └── tests.yaml
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

## Примечания

- **`DEBUG = True`** оставлен по умолчанию для удобства проверки
  (`/admin/`, отладочные страницы, статика).

</details>