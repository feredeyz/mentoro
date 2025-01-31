from datetime import datetime
from json import load
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