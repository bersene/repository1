import telebot
import requests
import json
from extensions import APIException, CurrencyConverter

# Загрузка токена Telegram-бота из конфига
TOKEN = 'Put  your token here'

# Создание экземпляра бота
bot = telebot.TeleBot(TOKEN)


# Класс для обработки ошибок API
class APIException(Exception):
    pass


# Класс для отправки запросов к API
class CurrencyConverter:
    @staticmethod
    def get_price(base, quote, amount):
        # Отправка запроса к API и получение данных о курсе валют
        response = requests.get(f'https://openexchangerates.org/api/latest.json?app_id= api key')

        # Проверка успешности запроса
        if response.status_code != 200:
            raise APIException('Ошибка при получении данных о курсе валют')

        # Парсинг ответа
        data = json.loads(response.text)

        # Проверка наличия информации о курсе валют в ответе
        if 'rate' not in data:
            raise APIException('Отсутствует информация о курсе валют')

        rate = float(data['rate'])
        converted_amount = rate * amount
        return converted_amount


# Обработчик команды /start или /help
@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    # Отправка инструкций по использованию бота
    instructions = 'Привет! Я бот для конвертации валют.\n\n' \
                   'Для получения цены на валюту, отправь мне сообщение в формате:\n' \
                   '<имя валюты, цену которой ты хочешь узнать> <имя валюты, в которой надо узнать цену первой валюты> <количество первой валюты>\n\n' \
                   'Например:\n' \
                   'USD RUB 100\n\n' \
                   'Для получения списка доступных валют используй команду /values.'
    bot.reply_to(message, instructions)


# Обработчик команды /values
@bot.message_handler(commands=['values'])
def handle_values(message):
    # Отправка информации о доступных валютах
    values = 'Доступные валюты:\n' \
             'USD - Доллар США\n' \
             'EUR - Евро\n' \
             'RUB - Российский рубль\n'
    bot.reply_to(message, values)


# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_text_message(message):
    try:
        # Получение данных из текстового сообщения
        input_data = message.text.split()
        if len(input_data) != 3:
            raise APIException('Неверный формат сообщения. Проверьте правильность ввода.')

        base = input_data[0].upper()
        quote = input_data[1].upper()
        amount = float(input_data[2])

        # Получение конвертированной суммы
        converted_amount = CurrencyConverter.get_price(base, quote, amount)

        # Отправка ответа пользователю
        response = f'{amount} {base} = {converted_amount} {quote}'
        bot.reply_to(message, response)

    except APIException as e:
        bot.reply_to(message, str(e))

    except Exception as e:
        bot.reply_to(message, 'Произошла ошибка при обработке запроса.')


# Запуск бота
bot.polling()
