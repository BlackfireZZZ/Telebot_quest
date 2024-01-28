import telebot
from telebot import types
import json

token = ""
bot = telebot.TeleBot(token)


gender_data = {}    # В этом словаре хранится пол пользователя (ключ - id пользователя, значение - пол)
first_message = {}      # В этом словаре хранится первое посланное пользователем сообщение (для корректной работы бота)
user_choices = {}       # В этом словаре хранится список выбранных пользователем ответов

file = open("bot_data.json", "r", encoding="utf-8")
data = json.load(file)
options = data["options"]
callback_list = data["callback_list"]
descriptions = data["descriptions"]
image_list = data["image_list"]

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, '-----------------------------------------------------------')
    user_id = message.chat.id
    user_choices[user_id] = []
    first_message[user_id] = message
    bot.send_message(user_id, f'Привет, {message.from_user.first_name}!')
    keyboard = types.InlineKeyboardMarkup()
    option1 = types.InlineKeyboardButton("М", callback_data="genderМ")
    option2 = types.InlineKeyboardButton("Ж", callback_data="genderЖ")
    keyboard.add(option1, option2)
    bot.send_message(user_id, "Ваш пол?", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('gender'))   # функция отвечает только на gender
def add_gender(call):
    user_id = call.message.chat.id
    if call.data == 'genderМ':  # устанавливаем пол пользователя
        gender_data[user_id] = ""
    else:
        gender_data[user_id] = "а"

    start = types.InlineKeyboardMarkup()
    start_but = types.InlineKeyboardButton("Начать", callback_data="start")
    start.add(start_but)
    bot.send_message(user_id, f'Начинаем?', reply_markup=start)


@bot.callback_query_handler(func=lambda call: True)     # функция отвечает на любой callback, кроме gender
def process_questions(call):
    try:
        user_choices[call.message.chat.id].append(call.data)
        if call.message.chat.id not in gender_data:
            gender_data[call.message.chat.id] = ""
        if call.data == "lose":
            process_lose(call)
        elif call.data == 'win':
            process_win(call)
        elif call.data == 'start_again':
            start(first_message[call.message.chat.id])
        elif call.data == 'stop':
            bot.send_message(call.message.chat.id, "Всего доброго!")
        else:
            user_id = call.message.chat.id
            if isinstance(image_list[call.data], list):
                if gender_data[user_id] == "а":
                    bot.send_photo(user_id, open(image_list[call.data][1], "rb"), caption=descriptions[call.data])
                else:
                    bot.send_photo(user_id, open(image_list[call.data][0], "rb"), caption=descriptions[call.data])
            else:
                bot.send_photo(user_id, open(image_list[call.data], "rb"), caption=descriptions[call.data])
            keyboard = types.InlineKeyboardMarkup()
            if isinstance(options[call.data], str):
                option = types.InlineKeyboardButton(options[call.data],
                                                    callback_data=callback_list[call.data][0])
                keyboard.add(option)
            else:
                for i in range(len(options[call.data])):
                    option = types.InlineKeyboardButton(options[call.data][i],
                                                        callback_data=callback_list[call.data][i])
                    keyboard.add(option)
            bot.send_message(user_id, "Что ты сделаешь?:", reply_markup=keyboard)
    except:     # обработка ошибок
        bot.send_message(call.message.chat.id, "Вы сломали бота! Попробуйте ещё раз сначала... \n"
                                               "(для этогот введите /start)")


def process_lose(call):     # функция обработки проигрыша
    file = open("users_choices.json", "w", encoding="utf-8")
    json.dump(user_choices, file)   # ответы игрока сохраняются в JSON файл
    file.close()

    user_id = call.message.chat.id
    bot.send_message(user_id, f"ТЫ ПРОИГРАЛ{gender_data[user_id]}")
    keyboard = types.InlineKeyboardMarkup()
    start_but = types.InlineKeyboardButton("Играть снова", callback_data="start_again")
    stop_but = types.InlineKeyboardButton("Закончить", callback_data="stop")
    keyboard.add(start_but, stop_but)
    bot.send_message(user_id, "Конец(", reply_markup=keyboard)


def process_win(call):      # функция обработки победы
    file = open("users_choices.json", "w", encoding="utf-8")
    json.dump(user_choices, file)   # ответы игрока сохраняются в JSON файл
    file.close()

    user_id = call.message.chat.id
    bot.send_message(user_id, f"ТЫ ВЫИГРАЛ{gender_data[user_id]}!!!")
    keyboard = types.InlineKeyboardMarkup()
    start_but = types.InlineKeyboardButton("Играть снова", callback_data="start_again")
    stop_but = types.InlineKeyboardButton("Закончить", callback_data="stop")
    keyboard.add(start_but, stop_but)
    bot.send_message(user_id, "Конец(", reply_markup=keyboard)


bot.polling(none_stop=True, interval=0)