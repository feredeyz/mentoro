import telebot as tb
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config_dev import TOKEN
from functions import (
    get_nearest_birthday, 
    get_bdays, 
    get_polls, 
    get_poll_variants, 
    get_poll, 
    update_votes,
    summ_arrays, 
    get_indexes,
    delete_poll_from_db,
    get_votes_by_user,
    create_table
)
from polls import Poll
import matplotlib.pyplot as plt
import schedule
import threading
import time
from datetime import datetime

# --------------------
# Инициализация бота
# --------------------
bot = tb.TeleBot(token=TOKEN)
create_table()

# --------------------
#     Переменные
# --------------------
ADMINS = []
COLORS = ['b', 'g', 'r', 'c', 'm', 'y', 'k']

# --------------------
# Клавиатуры
# --------------------
welcome_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
welcome_kb.add(
    KeyboardButton(text='Опросы'),
    KeyboardButton(text='Дни рождения')
)

bday_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
bday_kb.add(
    KeyboardButton(text='Все дни рождения'),
    KeyboardButton(text='Ближайшее день рождение'),
    KeyboardButton(text='Вернуться')
)

polls_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
polls_kb.add(
    KeyboardButton(text='Все опросы'),
    KeyboardButton(text='Вернуться')
)

admin_polls_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
admin_polls_kb.add(
    KeyboardButton(text='Все опросы'),
    KeyboardButton(text='Создать опрос'),
    KeyboardButton(text='Вернуться')
)

# --------------------
# Обработчики сообщений
# --------------------
@bot.message_handler(commands=["start"])
def welcome(msg: Message):
    bot.send_message(
        msg.chat.id,
        'Привет! Я - Кверти! Выбери, что ты хочешь, чтобы я сделал!',
        reply_markup=welcome_kb
    )
    with open('ids.txt', 'r+') as f:
        ids = f.read()
        if str(msg.chat.id) not in ids:
            f.write(str(msg.chat.id) + "\n")
            
@bot.message_handler(func=lambda msg: msg.text == "Вернуться")
def return_to_main(msg: Message):
    bot.send_message(
        msg.chat.id,
        'Привет! Я - Кверти! Выбери, что ты хочешь, чтобы я сделал!',
        reply_markup=welcome_kb
    )

# Дни рождения
@bot.message_handler(func=lambda msg: msg.text == 'Дни рождения')
def choose_bd_option(msg: Message):
    bot.send_message(msg.chat.id, text='Выбери, что именно ты хочешь!', reply_markup=bday_kb)

@bot.message_handler(func=lambda msg: msg.text == 'Все дни рождения')
def send_all_bdays(msg: Message):
    bdays = get_bdays()
    res = '\n'.join([f"{user_id} - {bdays[user_id]}" for user_id in bdays])
    bot.send_message(msg.chat.id, text=res)

@bot.message_handler(func=lambda msg: msg.text == 'Ближайшее день рождение')
def send_nearest_bday(msg: Message):
    bdays = get_bdays()
    bday = get_nearest_birthday(bdays)
    caption = f'Самое ближайшее день рождения у {bday[0]}. Оно будет {bday[1]}.'
    bot.send_message(msg.chat.id, text=caption)

# --------------------
# Функция автоматических поздравлений
# --------------------
def send_birthday_greetings():
    """Проверяет, есть ли сегодня дни рождения, и отправляет поздравление."""
    today = datetime.now().strftime("%d.%m")
    if today == '01.01':
        with open('ids.txt', 'r') as f:
            ids = f.readlines()
            for id in ids:
                id = id[:-1]
                bot.send_message(id, 'С Новым Годом!!')
    bdays = get_bdays()
    for person, bday_str in bdays.items():
        if bday_str[:5] == today:
            try:
                with open('ids.txt', 'r') as f:
                    ids = f.readlines()
                    for id in ids:
                        id = id[:-1]
                        bot.send_message(int(id), f'Поздравляем {person} с днём рождения!')
            except Exception as e:
                print(f"Ошибка отправки поздравления пользователю {person}: {e}")
schedule.every().day.at("00:00").do(send_birthday_greetings)

def run_schedule():
    """Функция для запуска планировщика задач в отдельном потоке."""
    while True:
        schedule.run_pending()
        time.sleep(60)

# --------------------
# Опросы
# --------------------
@bot.message_handler(func=lambda msg: msg.text == "Опросы" and msg.chat.id in ADMINS)
def admin_polls_options(msg: Message):
    bot.send_message(msg.chat.id, 'Выбери, что именно ты хочешь!', reply_markup=admin_polls_kb)

@bot.message_handler(func=lambda msg: msg.text == "Опросы")
def polls_options(msg: Message):
    bot.send_message(msg.chat.id, 'Выбери, что именно ты хочешь!', reply_markup=polls_kb)

@bot.message_handler(func=lambda msg: msg.text == 'Все опросы' and msg.chat.id in ADMINS)
def show_all_polls(msg: Message):
    polls = get_polls()
    if not polls:
        bot.send_message(msg.chat.id, 'Пока что нету никаких опросов!')
        return
    for poll in polls:
        poll_kb = InlineKeyboardMarkup(row_width=2)
        poll_kb.add(
            InlineKeyboardButton('Проголосовать', callback_data=f'vote_id{poll[0]}'),
            InlineKeyboardButton('Удалить опрос', callback_data=f'delete_poll{poll[0]}'),
            InlineKeyboardButton('Удалить голос', callback_data=f'delete_vote{poll[0]}'),
        )
        all_voters = len(summ_arrays(list(poll[2].values())))
        caption = f'Голосование: {poll[1]}\n'
        for idx, variant in enumerate(poll[2]):
            perc = round(len(poll[2][variant]) / all_voters, 2) * 100 if all_voters > 0 else 0
            caption += f'{idx + 1}. {variant} - {perc}%\n'
        bars = plt.barh([variant for variant in poll[2]], [len(poll[2][variant]) for variant in poll[2]])
        for idx, bar in enumerate(bars):
            if bar.get_width() != 0:
                bar.set_color(COLORS[idx + 1 % len(COLORS)])
        plt.savefig('poll.jpeg')
        plt.close()
        with open('poll.jpeg', 'rb') as photo:
            bot.send_photo(msg.chat.id, photo, caption=caption, reply_markup=poll_kb)

@bot.message_handler(func=lambda msg: msg.text == 'Все опросы')
def show_all_polls(msg: Message):
    polls = get_polls()
    if not polls:
        bot.send_message(msg.chat.id, 'Пока что нету никаких опросов!')
        return
    for poll in polls:
        poll_kb = InlineKeyboardMarkup(row_width=2)
        poll_kb.add(
            InlineKeyboardButton('Проголосовать', callback_data=f'vote_id{poll[0]}'),
            InlineKeyboardButton('Удалить голос', callback_data=f'delete_vote{poll[0]}'),
        )
        all_voters = len(summ_arrays(list(poll[2].values())))
        caption = f'Голосование: {poll[1]}\n'
        for idx, variant in enumerate(poll[2]):
            perc = round(len(poll[2][variant]) / all_voters, 2) * 100 if all_voters > 0 else 0
            caption += f'{idx + 1}. {variant} - {perc}%\n'
        bars = plt.barh([variant for variant in poll[2]], [len(poll[2][variant]) for variant in poll[2]])
        for idx, bar in enumerate(bars):
            if bar.get_width() != 0:
                bar.set_color(COLORS[idx + 1 % len(COLORS)])
        plt.savefig('poll.jpeg')
        plt.close()
        with open('poll.jpeg', 'rb') as photo:
            bot.send_photo(msg.chat.id, photo, caption=caption, reply_markup=poll_kb)
            
@bot.callback_query_handler(func=lambda call: 'delete_poll' in call.data and call.message.chat.id in ADMINS)
def delete_poll(call: CallbackQuery):
    poll_id = call.data[11:]
    delete_poll_from_db(poll_id)
    bot.answer_callback_query(call.id, 'Опрос успешно удалён')
    
@bot.callback_query_handler(func=lambda call: 'delete_vote' in call.data)
def get_deleted_vote(call: CallbackQuery):
    poll_id = call.data[11:]
    user = call.message.chat.id
    votes = get_votes_by_user(poll_id, user)
    if not votes:
        bot.answer_callback_query(call.id, 'Вы не голосовали.')
        return
    caption = 'У вас есть голоса за эти варианты. Напишите номер варианта, чтобы удалить ваш голос за него.\n'
    for idx, vote in enumerate(votes):
        caption += f'{idx + 1}. {vote}'
    bot.send_message(call.message.chat.id, caption)
    bot.register_next_step_handler(call.message, delete_vote_from_poll, poll_id, user, votes, call)
    
def delete_vote_from_poll(msg: Message, poll_id, user, votes, call):
    vote = msg.text
    if not vote.isdigit() or vote not in get_indexes(votes):
        bot.answer_callback_query(call.id, "Вы неправильно указали номер варианта.")
        return
    variants = get_poll_variants(poll_id)
    variant = votes[int(vote) - 1]
    variants[variant].remove(user)
    update_votes(poll_id, variants)
    bot.answer_callback_query(call.id, 'Вы успешно удалили свой голос.')

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
                    update_votes(poll[0], poll[2])
                    bot.answer_callback_query(call.id, "Вы успешно проголосовали!")
            if tmp == poll:
                bot.answer_callback_query(call.id, 'Вы уже голосовали за этот вариант.')
        else:
            all_voters = summ_arrays(list(variants.values()))
            if voter in all_voters:
                bot.answer_callback_query(call.id, "Вы уже голосовали.")
            else:
                poll[2][key].append(voter)
                update_votes(poll[0], poll[2])
                bot.answer_callback_query(call.id, "Вы успешно проголосовали!")

@bot.message_handler(func=lambda msg: msg.text == "Создать опрос" and msg.chat.id in ADMINS)
def create_poll(msg: Message):
    bot.register_next_step_handler(msg, process_poll_title)
    bot.send_message(msg.chat.id, "Напишите заголовок для опроса. Если вы хотите отменить, напишите ОТМЕНА.")

def process_poll_title(msg: Message):
    title = msg.text
    if title == 'ОТМЕНА':
        return
    bot.send_message(msg.chat.id, f'Заголовок - {title}. Напишите через запятую варианты для голосования')
    bot.register_next_step_handler(msg, process_poll_variants, title)
    
def process_poll_variants(msg: Message, title):
    if msg.text == 'ОТМЕНА':
        return
    variants = msg.text.split(', ')
    bot.send_message(msg.chat.id, f'Ваши варианты - {variants}. Можно ли выбирать несколько вариантов ответа? (Д/Н)')
    bot.register_next_step_handler(msg, process_poll_multiple, title, variants)

def multiple_check(msg, title, variants):
    if msg.text == 'ОТМЕНА':
        return
    bot.send_message(msg.chat.id, 'Вы неправильно ввели данные. Попробуйте ещё раз.')
    bot.register_next_step_handler(msg, process_poll_multiple, title, variants)

def process_poll_multiple(msg: Message, title, variants):
    if msg.text == 'ОТМЕНА':
        return
    if msg.text not in ("Д", "Н"):
        multiple_check(msg, title, variants)
    else:
        multiple = msg.text == "Д"
        poll = Poll(variants, multiple, title)
        poll.create_poll()
        bot.send_message(msg.chat.id, 'Опрос успешно создан!')

# --------------------
# Запуск планировщика в отдельном потоке
# --------------------
schedule_thread = threading.Thread(target=run_schedule, daemon=True)
schedule_thread.start()

# --------------------
# Запуск бота
# --------------------
bot.infinity_polling()
