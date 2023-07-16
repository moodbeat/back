# Бэкенд проекта "Moodbeat"

<details>
  <summary>Оглавление</summary>
  <ol>
    <li>
      <a href="#описание">Описание</a>
      <ul>
        <li><a href="#технологии">Технологии</a></li>
      </ul>
    </li>
    <li>
      <a href="#установка-и-запуск">Установка и запуск</a>
      <ul>
        <li><a href="#установка">Установка</a></li>
        <li><a href="#запуск">Запуск</a></li>
      </ul>
    </li>
    <li><a href="#использование">Использование</a></li>
    <li>
      <a href="#полезная-информация">Дополнительная информация</a>
      <ul>
        <li><a href="#переменные-окружения-env">Переменные окружения (.env)</a></li>
      </ul>
      <ul>
        <li><a href="#запуск-проекта-в-dev-режиме">Запуск проекта в dev режиме</a></li>
      </ul>
    </li>
  </ol>
</details>

<a name="описание"></a>

Проект является реализацией веб-сервиса, используемого для регулярного, оперативного и качественного контроля уровня работоспособности и психологического состояния работников.

В настоящее время работаем над совершенствованием системы и разработанных ранее функций.

### Технологии

[![Django][Django-badge]][Django-url]
[![Postgres][Postgres-badge]][Postgres-url]
[![Redis][Redis-badge]][Redis-url]
[![Celery][Celery-badge]][Celery-url]
[![Elasticsearch][Elasticsearch-badge]][Elasticsearch-url]
[![Nginx][Nginx-badge]][Nginx-url]

## Установка и Запуск

В данном разделе представлен минимальный набор инструкции,
необходимых для запуска приложения.

### Установка

1. Клонировать репозиторий и перейти в директорию для развертывания.

    ```shell
    git clone git@github.com:moodbeat/back.git
    cd back/docker/
    ```

2. Переименовать `.env.example` в `.env` и задать переменные окружения.
    > **Warning**:
    > Если не указаны значения для почтового сервера и DNS-адрес проекта
    > приложение работать полноценно не будет.

### Запуск

1. Выполнить запуск контейнеров Docker.

    ```shell
    sudo docker compose -f docker-compose-deploy.yaml up -d
    ```

2. Наполнить базу данных тестовыми записями.

    ```shell
    sudo docker compose -f docker-compose-deploy.yaml exec web python manage.py loaddata fixtures/test_data.json
    ```

3. При аутентификации использовать логин и пароль от учетной записи тестового пользователя-администратора.

    + логин
    ```
    admin@admin.admin
    ```
    + пароль
    ```
    DM94nghHSsl
    ```

## Использование

После выполнения инструкций, описанных в разделе
"[Установка и Запуск](#установка-и-запуск)", вы сможете получить
доступ к админке, перейдя по адресу http://localhost/admin.

Также по адресу http://localhost/api/v1/swagger/ доступна полная документация API.

## Полезная информация

Данный раздел содержит информацию, которая может быть полезна для разработчиков.

### Переменные окружения (.env)
```dotenv
# Переменные базы данных
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# Переменные Django
DJANGO_SECRET_KEY=https://djecrety.ir/
DJANGO_RESET_INVITE_SECRET_KEY=change
DJANGO_DEBUG=False

# время жизни refresh и access токенов
REFRESH_TOKEN_LIFETIME_DAYS=14
ACCESS_TOKEN_LIFETIME_MINUTES=30

# Переменные Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Переменные почтового сервера
DJANGO_SMTP=False
EMAIL_HOST=smtp.yourserver.com
EMAIL_HOST_USER=your@djangoapp.com
EMAIL_HOST_PASSWORD=yourpassword

# Переменная адреса проекта, куда будет приходить приглашение на регистрацию
SELF_HOST=https://example.com

# Переменные Elasticsearch
ELASTIC_HOST=elasticsearch
ELASTIC_PORT=9200

# Переменные Sentry
DEV_SERVICES=False
SENTRY_DSN=https://sentry.io/welcome/

# Переменные Celery
NOTIFICATIONS_AGE_DELETE=30

CELERY_BROKER=redis://redis:6379
CELERY_RESULT=redis://redis:6379

# Переменные бота
TELEGRAM_TOKEN=@BotFather
BASE_ENDPOINT=https://example.com/api/v1/  # адрес для обращения со стороны бота к RestAPI проекта
TIME_ZONE='Europe/Moscow'  # часовой пояс, должен быть одинаков в настройках Джанго и настройках бота
CONDITION_PERIOD_SEC=36000  # периодичность между оценкой своего состояния по 5-бальной шкале в секундах

```

### Запуск проекта в dev режиме

Для начала работы с проектом вам необходимо:
- иметь установленный менеджер зависимостей [Poetry](https://python-poetry.org/);
- [postgresql](https://www.postgresql.org/) 15+ версии;
- локально развернутые [elasticsearch](https://www.elastic.co/elasticsearch/) и [redis](https://redis.io/). Для удобства их развертывания воспользуйтесь приложенным [docker-compose](docker/docker-compose-dev.yaml).

После того как выполнены условия выше, скопируйте [example.env](docker/example.env) в [backend/conf](backend/conf/), переименуйте файл в **.env** и отредактируйте, особое внимание уделив указанным ниже строкам:

```dotenv
# имя бд, пользователя и пароль меняем в соответствии с создаными у себя в базе
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

DJANGO_DEBUG=True

# если поднимали воспользовавшись приложенным docker-compose конфигом
REDIS_HOST=localhost
REDIS_PORT=6379
ELASTIC_HOST=localhost
ELASTIC_PORT=9200
CELERY_BROKER=redis://localhost:6379
CELERY_RESULT=redis://localhost:6379

# если нужны логи (хранятся в backend/logs)
DEV_SERVICES=True

```

Далее перейдите в [/backend](backend) и выполните установку пакетов с зависимостями:
```bash
poetry install
```

Активируйте виртуальное окружение с установленными зависимостями:
```bash
poetry shell
```

Если потребности в постоянно активном виртуальном окружении не возникает, работайте с приложением по примеру ниже:
```bash
poetry run python manage.py runserver
```

После того как зависимости установлены и активированно виртуальное окружение, выполните миграции:
```bash
python manage.py migrate
```

По желанию можно загрузить в базу уже [предустановленные](backend/fixtures/test_data.json) данные и выполнить индексацию для elastisearch:
```bash
python manage.py loaddata fixtures/test_data.json
python manage.py search_index -f --rebuild
```
Важно отметить, что проводить индексацию необходимо лишь при заливке данных в обход приложения. При добавлении новых данных из приложения, индексация добавленного производится автоматически.

В приложенных к проекту [тестовых данных](backend/fixtures/test_data.json) уже есть учетная запись суперпользователя, с email **admin@admin.admin** и паролем **DM94nghHSsl**, однако если вы не загружали тестовые данные необходимо создать учетную запись суперпользователя:
```bash
python manage.py createsuperuser
```

После чего проект готов к работе по адресу указанному после запуска локального сервера:
```bash
python manage.py runserver
```
<!-- MARKDOWN LINKS & BADGES -->

[Django-url]: https://www.djangoproject.com/
[Django-badge]: https://img.shields.io/badge/Django-4.2-44b78b?style=for-the-badge&logo=django&logoColor=white

[Redis-url]: https://redis.io/
[Redis-badge]: https://img.shields.io/badge/Redis-7.0-d5362c?style=for-the-badge&logo=redis&logoColor=white

[Celery-url]: https://docs.celeryq.dev/en/stable/
[Celery-badge]: https://img.shields.io/badge/Celery-5.3.1-a0c24f?style=for-the-badge&logo=celery&logoColor=white

[Elasticsearch-url]: https://www.elastic.co/elasticsearch/
[Elasticsearch-badge]: https://img.shields.io/badge/Elasticsearch-8.8.0-101c3f?style=for-the-badge&logo=elasticsearch&logoColor=white

[Postgres-url]: https://www.postgresql.org/
[Postgres-badge]: https://img.shields.io/badge/Postgres-15.1-336791?style=for-the-badge&logo=postgresql&logoColor=white

[Nginx-url]: https://nginx.org
[Nginx-badge]: https://img.shields.io/badge/NGINX-1.21.3-419b45?style=for-the-badge&logo=nginx&logoColor=white
