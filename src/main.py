import telebot as tb
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import TOKEN
from functions import get_nearest_birthday, get_bdays, get_polls, get_poll_variants, get_poll, update_votes, summ_arrays, get_indexes
from polls import Poll
import matplotlib.pyplot as plt


# Initializations
bot = tb.TeleBot(token=TOKEN)

# Variables
ADMINS = [1297911832]

# Keyboards
welcome_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
welcome_kb.add(
    KeyboardButton(text='Опросы'),
    KeyboardButton(text='Дни рождения')
)

bday_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
bday_kb.add(
    KeyboardButton(text='Все дни рождения'),
    KeyboardButton(text='Ближайшее день рождение')
)

polls_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
polls_kb.add(
    KeyboardButton(text='Все опросы')
)

# Handlers
@bot.message_handler(commands=["start"])
def welcome(msg: Message):
    bot.send_message(msg.chat.id, 'Привет! Я - Кверти! Выбери, что ты хочешь, чтобы я сделал!', reply_markup=welcome_kb)

# ----------------
#   Дни рождения
# ----------------

    
@bot.message_handler(func=lambda msg: msg.text == 'Дни рождения')
def choose_bd_option(msg: Message):
    bot.send_message(msg.chat.id, text='Выбери, что именно ты хочешь!', reply_markup=bday_kb)

@bot.message_handler(func=lambda msg: msg.text == 'Все дни рождения')
def send_all_bdays(msg: Message):
    bdays = get_bdays()
    res = '\n'.join([f"{person} - {bdays[person]}" for person in bdays])
    bot.send_message(msg.chat.id, text=res)

@bot.message_handler(func=lambda msg: msg.text == 'Ближайшее день рождение')
def send_all_bdays(msg: Message):
    bdays = get_bdays()
    bday = get_nearest_birthday(bdays)
    caption = f'Самое ближайшее день рождения у {bday[0]}. Оно будет {bday[1]}.'
    bot.send_message(msg.chat.id, text=caption)


# ------------
#    Опросы
# ------------

@bot.message_handler(func=lambda msg: msg.text == "Опросы")
def polls_options(msg: Message):
    bot.send_message(msg.chat.id, 'Выбери, что именно ты хочешь!', reply_markup=polls_kb)
    
@bot.message_handler(func=lambda msg: msg.text == 'Все опросы')
def show_all_polls(msg: Message):
    polls = get_polls()
    for poll in polls:
        poll_kb = InlineKeyboardMarkup(row_width=2)
        poll_kb.add(
            InlineKeyboardButton(text='Проголосовать', callback_data=f'vote_id{poll[0]}')
        )
        all_voters = len(summ_arrays(list(poll[2].values())))
        caption = f'Голосование: {poll[1]}\n'
        for idx, variant in enumerate(poll[2]):
            perc = round(len(poll[2][variant]) / all_voters, 2) * 100 if all_voters > 0 else 0
            caption += f'{idx + 1}. {variant} - {perc}%\n'
        plt.barh([variant for variant in poll[2]], [sum(poll[2][variant]) for variant in poll[2]])
        plt.savefig('poll.jpeg')
        plt.close()
        with open('poll.jpeg', 'rb') as photo:
            bot.send_photo(msg.chat.id, photo, caption=caption, reply_markup=poll_kb)

@bot.callback_query_handler(func=lambda call: 'vote_id' in call.data)
def vote_for_poll(call: CallbackQuery):
    poll_id = call.data[7:].split('_')[0]
    poll = get_poll_variants(poll_id)
    res = ''
    for i, v in enumerate(poll):
        res += f'{i + 1}. {v}\n'
    bot.send_message(call.message.chat.id, 'Отлично! Теперь введи номер твоего выбора:\n' + res)
    bot.register_next_step_handler(call.message, process_vote, poll, poll_id, call)
    
def process_vote(msg, variants, poll_id, call):
    vote, voter = msg.text, msg.chat.id
    if not vote.isdigit() or vote not in get_indexes(variants):
        bot.answer_callback_query(call.id, "Вы неправильно указали номер варианта.")
    else:
        poll = get_poll(poll_id)
        keys = list(poll[2].keys())
        key = keys[int(vote) - 1]
        if poll[3]:
            tmp = poll
            for idx, variant in enumerate(variants.items()):
                if vote == str(idx + 1) and voter not in variant[1]:
                    poll[2][key].append(voter)
                    update_votes(poll)
                    bot.answer_callback_query(call.id, "Вы успешно проголосовали!")
            if tmp == poll:
                bot.answer_callback_query(call.id, 'Вы уже голосовали за этот вариант.')
        else:
            all_voters = summ_arrays(list(variants.values()))
            if voter in all_voters:
                bot.answer_callback_query(call.id, "Вы уже голосовали.")
            else:
                poll[2][key].append(voter)
                update_votes(poll)
                bot.answer_callback_query(call.id, "Вы успешно проголосовали!")

@bot.message_handler(commands=["cp"], func=lambda msg: msg.chat.id in ADMINS)
def create_poll(msg: Message):
    bot.register_next_step_handler(msg, process_poll_title)
    bot.send_message(msg.chat.id, "Напишите заголовок для опроса.")

def process_poll_title(msg: Message):
    title = msg.text
    bot.send_message(msg.chat.id, f'Заголовок - {title}. Напишите через запятую варианты для голосования')
    bot.register_next_step_handler(msg, process_poll_variants, title)
    
def process_poll_variants(msg: Message, title):
    variants = msg.text.split(', ')
    bot.send_message(msg.chat.id, f'Ваши варианты - {variants}. Можно ли выбирать несколько вариантов ответа? (Д/Н)')
    bot.register_next_step_handler(msg, process_poll_multiple, title, variants)

def multiple_check(msg, title, variants):
    bot.send_message(msg.chat.id, 'Вы неправильно ввели данные. Попробуйте ещё раз.')
    bot.register_next_step_handler(msg, process_poll_multiple, title, variants)

def process_poll_multiple(msg: Message, title, variants):
    if msg.text not in ("Д", "Н"):
        multiple_check(msg, title, variants)
    else:
        multiple = msg.text == "Д"
        poll = Poll(variants, multiple, title)
        poll.create_poll()
        bot.send_message(msg.chat.id, 'Опрос успешно создан!')
    

bot.polling(non_stop=True)
