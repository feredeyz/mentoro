from telebot import *
from telebot.types import Message
from config import TOKEN

bot = TeleBot(token=TOKEN)
    
@bot.message_handler(commands=["start"])
def welcome(msg: Message):
    bot.reply_to(msg, 'Привет!')

bot.polling(non_stop=True)

