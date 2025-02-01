from datetime import datetime
from json import load, dumps
import psycopg2 as sql


def get_nearest_birthday(data):
    today = datetime.today().date()
    birthdays_dates = {name: datetime.strptime(date, "%d.%m.%Y").date() for name, date in data.items()}
    current_year_birthdays = {name: date.replace(year=today.year) for name, date in birthdays_dates.items()}
    future_birthdays = {name: date for name, date in current_year_birthdays.items() if date >= today}
    
    if not future_birthdays:
        closest_name, closest_birthday = min(current_year_birthdays.items(), key=lambda x: x[1])
        closest_birthday = closest_birthday.replace(year=today.year + 1)
    else:
        closest_name, closest_birthday = min(future_birthdays.items(), key=lambda x: x[1])
    
    return closest_name, closest_birthday.strftime("%d.%m.%Y")

def get_bdays():
    with open('../bdays.json', "r") as f:
        return load(f)
    
def create_table():
    global conn, cur
    conn = sql.connect(
        dbname="",
        user="",
        password="",
        host="localhost",
        port="5432"
    )
    
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS polls (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    variants JSON NOT NULL,
    multiple BOOLEAN NOT NULL);
''')
    conn.commit()
    
    return conn, cur

def get_polls():
    cur.execute('SELECT * FROM polls')
    return cur.fetchall()

def get_poll(poll_id):
    cur.execute('SELECT * FROM polls WHERE id=%s', (poll_id))
    return cur.fetchone()

def update_votes(poll):
    cur.execute('UPDATE polls SET variants = %s WHERE id=%s', (dumps(poll[2]), poll[0]))
    conn.commit()

def get_poll_variants(poll_id):
    cur.execute('''
        SELECT * FROM polls WHERE id=%s
                ''', (poll_id))
    poll_variants = cur.fetchone()[2]
    return poll_variants
    
    
def check_vote(poll_id, variant_idx):
    cur.execute('''
        SELECT * FROM polls WHERE id=%s
                ''', (poll_id))
    poll = cur.fetchone()
    for i in poll[2][0]:
        pass
    
def summ_arrays(*args):
    tmp = []
    for i in args:
        tmp.extend(i)
    return tmp