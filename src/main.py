import telebot as tb
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton
from config import TOKEN
from json import load
from functions import get_nearest_birthday, get_bdays


# Initializations
bot = tb.TeleBot(token=TOKEN)

# Keyboards
welcome_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
welcome_kb.add(
    KeyboardButton(text='Опросы'),
    KeyboardButton(text='Дни рождения')
)

bday_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
bday_kb.add(
    KeyboardButton(text='Список всех дней рождения'),
    KeyboardButton(text='Ближайшее день рождение')
)

# Handlers
@bot.message_handler(commands=["start"])
def welcome(msg: Message):
    bot.send_message(msg.chat.id, 'Привет! Я - Квертик! Выбери, что ты хочешь, чтобы я сделал!', reply_markup=welcome_kb)
    
@bot.message_handler(func=lambda msg: msg.text == 'Дни рождения')
def choose_bd_option(msg: Message):
    bot.send_message(msg.chat.id, text='Выбери, что именно хочешь!', reply_markup=bday_kb)
#     bdays = get_bdays()
#     bday = get_nearest_birthday(bdays)
#     caption = '''
# Самое ближайшее день рождения - {bday}. Оно будет 
#     '''

@bot.message_handler(func=lambda msg: msg.text == 'Список всех дней рождения')
def send_all_bdays(msg: Message):
    bdays = get_bdays()
    res = '\n'.join([f"{person} - {bdays[person]}" for person in bdays])
    bot.send_message(msg.chat.id, text=res)

@bot.message_handler(func=lambda msg: msg.text == 'Ближайшее день рождение')
def send_all_bdays(msg: Message):
    bdays = get_bdays()
    bday = get_nearest_birthday(bdays)
    caption = f'''
Самое ближайшее день рождения - {bday[0]}. Оно будет {bday[1]}
    '''
    bot.send_message(msg.chat.id, text=caption)

bot.polling(non_stop=True)
