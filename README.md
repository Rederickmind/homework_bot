# Homework Telegram-bot

```
Телеграм-бот для отслеживания статуса проверки домашней работы на Яндекс.Практикум.
Присылает сообщения, когда статус изменен - взято в проверку, есть замечания, зачтено.

Также я использую его для оповещения о выполнении CI/CD других проектов.
```

### Технологии:
- Python 3.9
- python-dotenv 0.19.0
- python-telegram-bot 13.7

### Установка и запуск

**Клонируйте репозиторий:**

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:Rederickmind/homework_bot.git
```

```
cd homework_bot
```

**Установите и активируйте виртуальное окружение:**

```
python -m venv venv
```

* Если у вас Linux/macOS

    ```
    source venv/bin/activate
    ```

* Если у вас windows

    ```
    source venv/scripts/activate
    ```

**Обновите менеджер pip и установите зависимости**

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

### Необходимо заполнить env-файл для запуска

- токен профиля на Яндекс.Практикуме (Получить токен можно по адресу: https://oauth.yandex.ru/authorize?response_type=token&client_id=1d0b9dd4d652455a9eb710d450ff456a)
- токен телеграм-бота, полученный от @BotFather
- свой ID в телеграме (можно получить написав сообщение https://t.me/userinfobot)

```
touch .env
```

```
YANDEX_TOKEN = '...'
TELEGRAM_TOKEN = '...'
TELEGRAM_CHAT_ID = '...'
```

### Запуск проекта:

**Локально:**
```
python homework.py
```
**В Docker контейнере:**
```
docker compose up --build
```

- Levushkin Nikita,
- https://github.com/Rederickmind