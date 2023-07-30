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
        <li><a href="#использование-ngrok">Использование Ngrok</a></li>
      </ul>
      <ul>
        <li><a href="#запуск-проекта-в-dev-режиме">Запуск проекта в dev режиме</a></li>
      </ul>
    </li>
  </ol>
</details>

<a name="описание"></a>

Проект является реализацией сервиса, используемого для регулярного, оперативного и качественного контроля уровня работоспособности и психологического состояния работников.

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
  ```
  ```shell
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
3. Выполнить индексацию для elastisearch.
  ```bash
  sudo docker compose -f docker-compose-deploy.yaml exec web python manage.py search_index -f --rebuild
  ```

## Использование

После выполнения инструкций, описанных в разделе
"[Установка и Запуск](#установка-и-запуск)", вы сможете получить
доступ к админке, перейдя по адресу http://localhost/admin.

Пользователь с правами администратора (при использовании тестовой базы данных):

+ логин
```
admin@admin.admin
```
+ пароль
```
DM94nghHSsl
```

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

CELERY_BROKER=redis://redis:6379/1
CELERY_RESULT=redis://redis:6379/2

# email для писем из контактной формы
CONTACT_EMAIL=mail@example.com

# Переменные бота
TELEGRAM_TOKEN=@BotFather
BASE_ENDPOINT=https://example.com/api/v1/  # адрес для обращения со стороны бота к RestAPI проекта
TIME_ZONE=Europe/Moscow  # часовой пояс - должен быть одинаков в настройках Джанго и настройках бота
CONDITION_PERIOD_SEC=36000  # периодичность в секундах между оценкой своего состояния по 5-бальной шкале
BOT_NAME=example_bot_name # имя пользователя бота
BOT_INVITE_TIME_EXPIRES_MINUTES=10 # время действия кода отправляемого на email для авторизации в боте
WEB_HOOK_MODE=False  # запуск бота в режиме webhook - True, в режиме polling - False
WEB_HOOK_HOST=https://example.com  # домен с ssl, на котором развернут бот
WEB_APP_PORT=5000  # порт на котором будет "слушать" бот в режиме webhook
```

### Использование Ngrok

Этот раздел будет полезен при запуске проекта в dev-режиме, если у вас нет доменного имени с установленным SSL-сертификатом.

Ngrok — инструмент, который позволяет создавать временный общедоступный адрес (туннель) для вашего локального сервера,
находящимся за NAT или брандмауэром.

Подробнее: https://ngrok.com/

1. Установить Ngrok, следуя официальным инструкциям.

  https://ngrok.com/download

2. Запустить туннель.

  ```shell
  ngrok http 80
  ```

3. Задать значение переменным окружения (.env).

  В процессе разработки при локальном развертывании контейнеров `Docker` необходимо указать предоставленный `ngrok` туннель для данных переменных окружения.

  > **Warning**:
  > Обратите внимание, что указанный ниже адрес туннеля `https://1234-56-78-9.eu.ngrok.io`
  > является примером и должен быть заменен.

  ```dotenv
  SELF_HOST=https://1234-56-78-9.eu.ngrok.io
  WEB_HOOK_HOST=https://1234-56-78-9.eu.ngrok.io
  BASE_ENDPOINT=https://1234-56-78-9.eu.ngrok.io/api/v1/  # отметьте, что здесь дополнительно указывается принадлежность к API и его версия `api/v1/`
  ```

### Запуск проекта в dev режиме

Для начала работы с проектом вам необходимо:
- должен быть запущен Ngrok в соответствии с [Использование Ngrok](#использование-ngrok)
- иметь установленный менеджер зависимостей [Poetry](https://python-poetry.org/);
- в директории [docker/](docker/) переименовать файл `.env.example` в `.env` в соответствии с [Переименовать `.env.example` в `.env`](#установка) и задать переменные окружения, особое внимание уделив указанным ниже строкам:

```dotenv
DJANGO_DEBUG=True

# если поднимали воспользовавшись приложенным docker-compose конфигом
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

REDIS_HOST=localhost
REDIS_PORT=6379
ELASTIC_HOST=localhost
ELASTIC_PORT=9200
CELERY_BROKER=redis://localhost:6379/1
CELERY_RESULT=redis://localhost:6379/2

# при запуске бота и использовании Ngrok
SELF_HOST=https://1234-56-78-9.eu.ngrok.io
WEB_HOOK_HOST=https://1234-56-78-9.eu.ngrok.io
BASE_ENDPOINT=https://1234-56-78-9.eu.ngrok.io/api/v1/

# если нужны логи (хранятся в backend/logs)
DEV_SERVICES=True
```

- локально развернуть [nginx](https://nginx.org/), [elasticsearch](https://www.elastic.co/elasticsearch/), [postgresql](https://www.postgresql.org/) и [redis](https://redis.io/). Для удобства их развертывания воспользуйтесь приложенным [docker-compose](docker/docker-compose-dev.yaml).

После того как выполнены условия выше, скопируйте [.env](docker/.env) в [backend/conf](backend/conf/) и [bot](bot/).

Далее необходимо последовательно выполнить установку зависимостей в директориях [/backend](backend) и [/bot](bot):
```bash
cd backend/ && poetry install && cd ../bot/ && poetry install
```

В отдельных терминалах активируйте виртуальные окружения бэкенда и бота с установленными зависимостями:

- терминал 1:
  ```bash
  cd backend && poetry shell
  ```
- терминал 2:
  ```bash
  cd bot && poetry shell
  ```

Если потребности в постоянно активном виртуальном окружении не возникает, работайте с приложением по примеру ниже:
```bash
poetry run python manage.py runserver
```

После того как зависимости установлены и активированно виртуальное окружение, выполните миграции из терминала бэкенда приложения:
```bash
python manage.py migrate
```

По желанию можно загрузить в базу уже [предустановленные](backend/fixtures/test_data.json) данные и выполнить индексацию для elastisearch:
```bash
python manage.py loaddata fixtures/test_data.json
python manage.py search_index -f --rebuild
```
  > **Warning**:
  > Обратите внимание, что проводить индексацию необходимо лишь при заливке данных в обход приложения.
  > При добавлении новых данных из приложения, индексация добавленного производится автоматически.

В приложенных к проекту [тестовых данных](backend/fixtures/test_data.json) уже есть учетная запись суперпользователя, с email **admin@admin.admin** и паролем **DM94nghHSsl**, однако если вы не загружали тестовые данные необходимо создать учетную запись суперпользователя:
```bash
python manage.py createsuperuser
```

Запустите бэкенд проект командой ниже. Он будет готов к работе по адресу указанному в терминале после запуска локального сервера:
```bash
python manage.py runserver
```

Из терминала бота для его запуска выполните следующую команду:
```bash
python main.py
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
