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

# Переменная DNS-адреса проекта
SELF_HOST=https://example.com
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
