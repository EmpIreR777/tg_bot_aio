from faker import Faker


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
