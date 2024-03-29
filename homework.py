import logging
import os
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

import exceptions

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logging.info('Сообщение отправлено')
    except Exception as error:
        logging.exception(f'Ошибка отправки сообщения: {error}')


def get_api_answer(current_timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    params = {'from_date': current_timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except Exception:
        logging.exception('Сбой запроса к эндпойнту')
    if response.status_code != HTTPStatus.OK:
        raise exceptions.APIResponseError('Статус отличен от 200')
    return response.json()


def check_response(response):
    """Проверяет ответ API на корректность."""
    try:
        homework_list = response['homeworks']
    except exceptions.CheckResponseError as error:
        logging.exception(f'Ошибка доступа: {error}')
    if len(homework_list) == 0:
        raise exceptions.CheckResponseError('Список домашних работ пуст')
    if not isinstance(homework_list, list):
        raise exceptions.HomeWorkTypeError('Домашки приходят не списком')
    return homework_list


def parse_status(homework):
    """Извлекает из информации о конкретной домашней работе её статус."""
    try:
        homework_name = homework.get('homework_name')
        homework_status = homework.get('status')
    except exceptions.HomeWorkParseError:
        if homework_name is None:
            raise exceptions.ParseStatusError('Неизвестный статус домашки')
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет доступность необходимых переменных окружения."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def main():
    """Основная логика работы бота."""
    logging.debug('Бот запущен')
    if not check_tokens():
        logging.critical('Отсутствует переменная среды')
        raise exceptions.MissingRequiredTokenError(
            'Отсутствует один из токенов'
        )
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = 0
    previous_status = None
    previous_error = None

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            homework_status = parse_status(homework[0])
            if homework_status != previous_status:
                previous_status = homework_status
                send_message(bot, homework_status)
            else:
                logging.debug('Нет обновлений')

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            if previous_error != str(error):
                previous_error = str(error)
                send_message(bot, message)
            logging.exception(message)

        else:
            logging.debug('Обновлений нет')
        time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
