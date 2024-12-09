from faker import Faker
import pytz


def get_random_person():
    # Создаем объект Faker с русской локализацией
    fake = Faker('ru_RU')

    # Генерируем случайные данные пользователя
    user = {
        'name': fake.name(),
        'address': fake.address(),
        'email': fake.email(),
        'phone_number': fake.phone_number(),
        'birth_date': fake.date_of_birth(),
        'company': fake.company(),
        'job': fake.job(),
    }
    return user


def get_msc_date(utc_time):
    # Задаем московский часовой пояс
    moscow_tz = pytz.timezone('Europe/Moscow')
    # Переводим время в московский часовой пояс
    moscow_time = utc_time.astimezone(moscow_tz)
    return moscow_time
