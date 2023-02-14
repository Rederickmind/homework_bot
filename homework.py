import http
import logging
import os
import sys
import time
from http import HTTPStatus
from logging import StreamHandler

import requests
import telegram
from dotenv import load_dotenv
from telegram import TelegramError

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = StreamHandler(stream=sys.stdout)
logger.addHandler(handler)
formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(message)s'
)
handler.setFormatter(formatter)


PRACTICUM_TOKEN = os.getenv('YANDEX_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Проверка наличия токенов."""
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))


def send_message(bot, message):
    """Отправка сообщений."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug(f'Бот отправил сообщение {message}')
    except TelegramError as error:
        logger.error(f'Сообщение не отправленно: {error}')


def get_api_answer(timestamp):
    """Получение ответа от API."""
    params = {'from_date': timestamp}
    try:
        api_answer = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params
        )
        if api_answer.status_code != HTTPStatus.OK:
            message = (
                f'Эндпоинт {ENDPOINT} недоступен. '
                f'Код ответа API: {api_answer.status_code}'
            )
            logger.error(message)
            raise http.exceptions.HTTPError()
        return api_answer.json()
    except requests.exceptions.ConnectionError:
        logger.error('Ошибка подключения')
    except requests.exceptions.RequestException as request_error:
        logger.error(f'Ошибка запроса {request_error}')


def check_response(response):
    """Проверка ответа."""
    if not isinstance(response, dict):
        logger.debug('Ответ не является словарем')
        raise TypeError('Ответ не является словарем')
    if 'homeworks' not in response:
        logger.debug('Ответ не содержит ключ homeworks')
        raise KeyError('Ответ не содержит ключ homeworks')
    if 'current_date' not in response:
        logger.debug('Ответ не содержит ключ current_date')
        raise KeyError('Ответ не содержит ключ current_date')
    homeworks = response['homeworks']
    if not isinstance(homeworks, list):
        logger.debug('homeworks не возвращается в виде списка')
        raise TypeError('homeworks не возвращается в виде списка')
    return homeworks


def parse_status(homework):
    """Извлечение статуса домашней работы."""
    if 'homework_name' not in homework:
        logger.debug('Ответ не содержит ключ homework_name')
        raise KeyError('Ответ не содержит ключ homework_name')
    homework_name = homework.get('homework_name')
    logger.debug(f'Название домашки: {homework_name}')
    homework_status = homework.get('status')
    logger.debug(f'Статус домашки: {homework_status}')
    if homework_status not in HOMEWORK_VERDICTS:
        raise KeyError('Недокументированный статус домашней '
                       'работы в ответе API')
    verdict = HOMEWORK_VERDICTS.get(homework_status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if check_tokens() is False:
        logger.critical('Отсутствуют необходимые токены.')
        raise SystemExit

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    # timestamp = 0
    current_report = {}
    prev_report = {}

    while True:
        try:
            response = get_api_answer(timestamp)
            logger.debug(f'Ответ функции get_api_answer: {response}')
            check = check_response(response)
            if len(check) == 0:
                logger.info('Нет домашних заданий на проверке')
                message = 'Нет домашних заданий на проверке'
                current_report['status'] = 'Нет домашних заданий на проверке'
                if current_report != prev_report:
                    send_message(bot, message)
                    prev_report = current_report.copy()
                else:
                    logger.debug('Статус не изменился с прошлой проверки')
            else:
                logger.debug(f'Ответ check_response: {check}')
                message = parse_status(check[0])
                logger.debug(f'Ответ parse_status {message}')
                current_report['status'] = message
                if current_report != prev_report:
                    send_message(bot, message)
                    prev_report = current_report.copy()
                else:
                    logger.debug('Статус не изменился с прошлой проверки')
        except Exception as error:
            message = f'Сбой в работе программы {error}'
            logger.error(message)
            current_report['status'] = message
            if current_report != prev_report:
                send_message(bot, message)
                prev_report = current_report.copy()
        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
