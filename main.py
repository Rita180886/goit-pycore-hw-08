from collections import UserDict
from datetime import datetime, date, timedelta
import pickle

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)
    
class Name(Field):
    pass

# Клас для збереження номера телефону (з перевіркою)
class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Номер телефону повинен містити рівно 10 цифр")
        super().__init__(value)

class Birthday(Field):
    DATE_FORMAT = "%d.%m.%Y"

    def __init__(self, value):
        try:
            d = datetime.strptime(value, self.DATE_FORMAT).date()
        except ValueError:
            raise ValueError("Неправильний формат дати. Використовуйте формат ДД.ММ.РРРР.")
        super().__init__(d)

    def __str__(self):
        return self.value.strftime(self.DATE_FORMAT)

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                return True
            return False
        
    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:
            if p.value == old_phone:
                new_p = Phone(new_phone)
                p.value = new_p.value
                return True
        return False
        
    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None
    
    def add_birthday(self, birthday_str):
        self.birthday = Birthday(birthday_str)
    
    def __str__(self):
        phones = ', '.join(p.value for p in self.phones)
        birthday = str(self.birthday) if self.birthday else "-"
        return f"Contact name: {self.name.value}, phones: {phones}, birthday: {birthday}"
    
        
class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)
    
    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def upcoming_birthdays(self, within_days=7):
        today = date.today()
        result = []

        for record in self.data.values():
            if record.birthday is None:
                continue

            bday = record.birthday.value.replace(year=today.year)
            if bday < today:
                bday = bday.replace(year=today.year + 1)

            diff = (bday - today).days
            if 0 <= diff <= within_days:
                if bday.weekday() >= 5:
                    bday = bday + timedelta(days=7 - bday.weekday())
                result.append(f"{record.name.value}: {bday.strftime(Birthday.DATE_FORMAT)}")

        return result
def save_data(book, filename="addressbook.pkl"):
        with open(filename, "wb") as f:
            pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
        try:
            with open(filename, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return AddressBook()

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (KeyError, ValueError, IndexError) as e:
            return str(e)
    return wrapper

# Commands
@input_error
def add_contact(args, book):
    name, phone = args[0], args[1]
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    record.add_phone(phone)
    return message

@input_error
def change_phone(args, book):
    name, old_p, new_p = args[0], args[1], args[2]
    record = book.find(name)
    if record.edit_phone(old_p, new_p):
        return "Номер змінено."
    return "Старий номер не знайдено."

@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    phones = ", ".join(p.value for p in record.phones) if record.phones else "-"
    return f"{name}: {phones}"

def show_all(book):
        if not book.data:
             return "Контактів немає."
        return "\n".join(str(record) for record in book.data.values())

@input_error
def add_birthday_cmd(args, book):
    if len(args) < 2:
        return "Помилка: введіть ім'я та дату наприклад: add-birthday John 25.12.1990"
    
    name, bday = args[0], args[1]
    record = book.find(name)

    if record is None:
        return "Спочатку додайте контакт командою add."
    
    record.add_birthday(bday)
    return "День народження додано."

@input_error
def show_birthday_cmd(args, book):
    if len(args) < 1:
        return "Помилка: введіть ім'я, наприклад: show-birthday John"
    
    name = args[0]
    record = book.find(name)

    if record is None:
        return "Контакт не знайдено."
    
    if record.birthday is None:
        return "День народження не вказано."
    
    return f"{name}: {record.birthday}"

def birthdays_cmd(book):
    result = book.upcoming_birthdays()
    if not result:
        return "Немає привітань на наступний тиждень."
    return "\n".join(result)

def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        if not user_input.strip():
            continue

        parts = user_input.split()
        cmd = parts[0]
        args = parts[1:]

        if cmd in ("exit", "close"):
            save_data(book)
            print("Good bye!")
            break
        elif cmd == "hello":
            print("How can I help you?")
        elif cmd == "add":
            print(add_contact(args, book))
        elif cmd == "change":
            print(change_phone(args, book))
        elif cmd == "phone":
            print(show_phone(args, book))
        elif cmd == "all":
            print(show_all(book))
        elif cmd == "add-birthday":
            print(add_birthday_cmd(args, book))
        elif cmd == "show-birthday":
            print(show_birthday_cmd(args, book))
        elif cmd == "birthdays":
            print(birthdays_cmd(book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()