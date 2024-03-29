# Foodgram — социальная сеть для обмена рецептами. (Яндекс.Практикум)

## Основные функции проекта
- регистрация пользователей, подписка на пользователей
- создание записей рецептов, с тегами и ингредиентами
- редактирование и удаление записей, просмотр чужих, фильтрация по тегам

## Стек
### Frontend
  - React
### Backend
  - Python
  - Django
  - DRF
  - Nginx
  - gunicorn

## Развертывание проекта и виртуального окружения
- создание локальной копии: 'git clone <SSH-ссылка>'
- создание виртуального окружения: 'python3 -m venv env'
- активация окружения: 'source env/bin/activate'
- установка необходимых пакетов 'pip install -r requirements.txt`

## Прописывание переменных окружения
- в корне проекта создать файл .env
- в файле .env прописать:
  - SECRET_KEY в формате: 'SECRET_KEY = "<ваш_ключ>"'
  - ALLOWED_HOSTS в формате: 'ALLOWED_HOSTS = "<адреса и IP через пробел без кавычек>"'
  - POSTGRES_USER в формате: 'POSTGRES_USER = "<имя_пользователя>"'
  - POSTGRES_PASSWORD в формате: 'POSTGRES_PASSWORD = "<пароль_бд>"'
  - POSTGRES_DB в формате: 'POSTGRES_DB = "<имя_бд>"'
  - DB_HOST в формате: 'DB_HOST = "<адрес_хоста>"'
  - DB_PORT в формате: 'DB_PORT = <порт_хоста>'
  - DEBUG в формате: 'DEBUG = <булево_значение_режима_отладки>'

## Автор
[Алекс Бро](https://github.com/avbrotune/)

## Сервер
https://nomatter.hopto.org/
Логин 1@1.ru
Пароль 1