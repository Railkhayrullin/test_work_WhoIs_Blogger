from random import randint
from peewee import *
from datetime import date, timedelta

# связь с уже существующей базой данных с именем 'test_1'
db = PostgresqlDatabase(database='test_1', user='postgres', password='1', host='localhost')


# Функция для генерации данных таблицы Users(userId, age) и загрузки в БД
def get_users():
    users = list()
    for _ in range(30):
        age = str(randint(18, 50))
        user = {'age': age}
        users.append(user)

    db.create_tables([Users])
    with db.atomic():
        for row in users:
            Users.create(**row)


# Функция для генерации данных таблицы Purchases(purchaseId, userId, itemId, date) и загрузки в БД
def get_purchases():
    purchases = list()
    d1 = date(2016, 1, 1)
    d2 = date(2020, 10, 20)
    days = (d2 - d1).days
    for _ in range(3000):
        user_id = randint(1, 30)
        item_id = randint(1, 10)
        date_of_purchase = str(d1 + timedelta(randint(1, days)))
        purchase = {'user_id': user_id,
                    'item_id': item_id,
                    'date': date_of_purchase}
        purchases.append(purchase)

    db.create_tables([Purchases])
    with db.atomic():
        for row in purchases:
            Purchases.create(**row)


# Функция для генерации данных таблицы Items (itemId, price) и загрузки в БД
def get_items():
    items = list()
    for i in range(1000, 11000, 1000):
        price = i
        item = {'price': price}
        items.append(item)

    db.create_tables([Items])
    with db.atomic():
        for row in items:
            Items.create(**row)


# Создал эту модель чтобы при создании новых моделей не дописывать в них "class Meta"
class BaseModel(Model):
    class Meta:
        database = db


# Модель таблицы Users
class Users(BaseModel):
    user_id = AutoField()
    age = IntegerField()


# Модель таблицы Items
class Items(BaseModel):
    item_id = AutoField()
    price = IntegerField()


# Модель таблицы Purchases
class Purchases(BaseModel):
    purchase_id = AutoField()
    user_id = ForeignKeyField(Users)
    item_id = ForeignKeyField(Items)
    date = DateField()


def main():
    db.connect()
    get_users()
    get_items()
    get_purchases()


if __name__ == '__main__':
    main()
