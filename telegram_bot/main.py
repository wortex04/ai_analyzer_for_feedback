import requests
import telebot
from telebot import types
import json
import datetime
from config import token_bot

TOKEN = token_bot

# Создание экземпляра бота
bot = telebot.TeleBot(TOKEN)

# Словарь для хранения текущего состояния каждого пользователя
user_state = {}

# Словарь для хранения отзывов пользователей
user_reviews = {}

states = {}

categories = ['Основы программирования', 'Продвинутые техники программирования',
              'Новейшие тенденции в IT', 'ChatGPT для обучения',
              'Управление персоналом', 'Знакомство с языком Python',
              'Java api браузеров']


# Обработчик команды /start
@bot.message_handler(commands=['start', 'go'])
def start_handler(message):

    msg = bot.send_message(message.chat.id, "Привет, это бот для ваших отзывов. Отправь свой id для регистрации")
    bot.register_next_step_handler(msg, auth)


def create_categories_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    for i in range(0, len(categories), 2):
        category1 = categories[i]
        category2 = categories[i + 1] if i + 1 < len(categories) else ""
        keyboard.add(types.KeyboardButton(category1), types.KeyboardButton(category2))
    return keyboard

def ready_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.row("1", "2", "3", "4", "5")
    keyboard.row("6", "7", "8", "9", "10")
    return keyboard


def create_review_markup():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text="Оставить отзыв"))

    return keyboard


def auth(message):
    data = message.text
    user_id = message.from_user.id

    # check = users.find_one({ # проверяем наличие в базе комбинации логина и пароля
    #     'username': str(data['username']),
    #     'password': str(data['password']),
    # })

    check = True

    if check is None:  # если такой комбинации не существует, ждём команды /start Опять
        bot.send_message(message.chat.id, r'Неправильно введен логин\пароль')

    else:  # а если существует, переходим к следующему шагу
        msg = bot.send_message(message.chat.id, 'Авторизация прошла успешно', reply_markup=create_review_markup())
        states[user_id] = "authorized"


@bot.message_handler(
    func=lambda message: message.text == "Оставить отзыв" and states.get(message.from_user.id) == "authorized")
def ready_counter(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, "На шкале от 1 до 10, насколько вы готовы поделиться вашим мнением о вебинаре?",
                     reply_markup=ready_keyboard())
    states[user_id] = "answering"


@bot.message_handler(
    func=lambda message: states.get(message.from_user.id) == "answering")
def handle_category_selection(message):
    user_id = message.from_user.id
    if int(message.text) > 5:

        bot.send_message(message.chat.id, 'О каком вебинаре Вы хотите рассказать?',
                         reply_markup=create_categories_keyboard())
        states[user_id] = "new_review"
    else:
        bot.send_message(message.chat.id, 'Возвращайтесь, если захотите отсавить отзыв',reply_markup=create_review_markup())
        states[user_id] = "authorized"


@bot.message_handler(
    func=lambda message: message.text in categories and states.get(message.from_user.id) == "new_review")
def handle_category_selection(message):
    user_id = message.from_user.id
    # TODO set web in json
    message_time = message.date
    user_reviews[user_id] = message_time
    user_reviews[user_id] = {}
    message_time = datetime.datetime.fromtimestamp(message_time)
    formatted_time = message_time.strftime('%Y-%m-%d %H:%M:%S')

    user_reviews[user_id]['timestamp'] = formatted_time
    user_reviews[user_id]['question_1'] = message.text
    bot.send_message(message.chat.id, f"Что вам больше всего понравилось в теме вебинара и почему?",
                     reply_markup=telebot.types.ReplyKeyboardRemove())
    states[user_id] = "question_1"


@bot.message_handler(func=lambda message: states.get(message.from_user.id) == "question_1")
def handle_question_1(message):

    user_id = message.from_user.id
    user_reviews[user_id]['question_2'] = message.text
    # TODO set answer
    bot.send_message(user_id,
                     "Были ли моменты в вебинаре, которые вызвали затруднения в понимании материала? Можете описать их?")
    states[user_id] = "question_2"


# Обработчик ответа на второй вопрос
@bot.message_handler(func=lambda message: states.get(message.from_user.id) == "question_2")
def handle_question_2(message):
    user_id = message.from_user.id
    user_reviews[user_id]['question_3'] = message.text

    # TODO set answer
    bot.send_message(message.chat.id,
                     "Какие аспекты вебинара, по вашему мнению, нуждаются в улучшении и какие конкретные изменения вы бы предложили?")
    states[user_id] = "question_3"


# Обработчик ответа на третий вопрос
@bot.message_handler(func=lambda message: states.get(message.from_user.id) == "question_3")
def handle_question_3(message):
    user_id = message.from_user.id
    user_reviews[user_id]['question_4'] = message.text
    # TODO set answer
    bot.send_message(message.chat.id,
                     "Есть ли темы или вопросы, которые вы бы хотели изучить более подробно в следующих занятиях?")
    states[user_id] = "question_4"


# Обработчик ответа на четвертый вопрос
@bot.message_handler(func=lambda message: states.get(message.from_user.id) == "question_4")
def handle_question_3(message):
    user_id = message.from_user.id
    user_reviews[user_id]['question_5'] = message.text
    # TODO set
    states[user_id] = "authorized"
    bot.send_message(message.chat.id, "Спасибо за ответы!", reply_markup=create_review_markup())

    with open('answer.json', 'a', encoding='utf-8') as f:
        json.dump(user_reviews[user_id], f, ensure_ascii=False)
        url = "http://127.0.0.1:8000/api/v1/telegram_api/extend_csv"
        print(user_reviews[user_id])
        response = requests.post(url, json=user_reviews[user_id])

        print(response)

        del(user_reviews[user_id])
        f.write("\n")


# Обработчик всех неизвестных сообщений
@bot.message_handler(func=lambda message: True)
def handle_unknown(message):
    user_id = message.from_user.id
    bot.reply_to(message, "Извините, я не понимаю вашего сообщения. Пожалуйста, воспользуйтесь доступными командами или функциональностью бота.", reply_markup=create_review_markup())
    states[user_id] = "authorized"


bot.polling()