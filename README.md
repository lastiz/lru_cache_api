# LRU Cache API

Least Recently Used (LRU) cache с поддержкой Time-To-Live (TTL).

## Требования

- Docker
- Docker Compose
- Poetry (для запуска тестов)
- Make (для использования с Makefile)

## Установка (Make)

1. Склонировать репозиторий
2. Создать файл .env в корне проекта (Смотрите .env.example)
3. Запустить команду ```make up```

## Установка
1. Склонировать репозиторий
2. Создать файл .env в корне проекта (Смотрите .env.example)
3. docker compose up -d

## Тестирование
1. Склонировать репозиторий
2. Создать файл .env в корне проекта (Смотрите .env.example)
3. Создать окружение и установить зависимости ```poetry env use python```, ```poetry install --no-root```
4. Зайти в окружение (может потребоваться плагин для poetry-shell) ```poetry shell```
5. Запустить ```pytest -svv```
