import telebot
from telegram_bot import token

bot = telebot.TeleBot(token)


def log(message):
    from datetime import datetime
    print('\n ==================')
    print(datetime.now())
    print('Сообщение от %s %s. \n Текст - %s' %(message.from_user.first_name,
                                                message.from_user.last_name,
                                                message.text))

@bot.message_handler(commands=['action'])
def handle_text(message):
    bot.send_message(message.chat.id, '???')
    log(message)

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_markup = telebot.types.ReplyKeyboardMarkup(True,True)
    user_markup.row('Спрятать клавиатуру')
    user_markup.row('Раз','Два')
    user_markup.row('Три','Четыре','Пять')
    bot.send_message(message.from_user.id,'Привет, вот клавиатура..',reply_markup=user_markup)

@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text == 'привет':
        bot.send_message(message.chat.id, 'Привет')
        log(message)
    elif message.text == 'пока':
        bot.send_message(message.chat.id, 'Давай, пока')
        log(message)

@bot.message_handler(content_types=['Спрятать клавиатуру'])
def handle_text(message):
    user_markup = telebot.types.ReplyKeyboardHide()
    bot.send_message(message.from_user.id,reply_markup=user_markup)

bot.polling(none_stop=True, interval=0)