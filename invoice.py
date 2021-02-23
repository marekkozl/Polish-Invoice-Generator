# -*- coding: utf-8 -*-

from InvoiceGenerator.api import Invoice, Item, Client, Provider
from InvoiceGenerator.pdf import SimpleInvoice
from faker import Faker
import random
from datetime import datetime
from datetime import timedelta
import locale
import csv
from conf import *

locale.setlocale(locale.LC_ALL, '')

fake = Faker(FAKER_REGION)

def get_random_invoice_dates():
    date_start = fake.date_between(start_date='-10y', end_date='today')
    date_end = fake.date_between_dates(
        date_start, date_start + timedelta(days=random.randint(0, 30)))
    return date_start.strftime("%m/%d/%Y"), date_end.strftime("%m/%d/%Y")


def get_random_provider():
    street, address = fake.address().split('\n')
    provider = Provider(name=fake.company(),
                        address1=street,
                        address2=address,
                        nip=fake.itin(),
                        bank_data=None,
                        bank_account=None,
                        payment_terms=None) # bank_account=fake.pyint(min_value=10000000000000000000000000, max_value=99999999999999999999999999))
    return provider


def get_random_client():
    person = fake.profile()
    street, address = person.get('residence').split('\n')
    client = Client(name=person.get('company'),
                    address1=street,
                    address2=address,
                    nip=fake.itin())
    return client


def get_random_category():
    return random.choice(CRAWLER_CATEGORIES)

def get_random_product_from_csv(category_list):
    product = [[]]
    index = 0
    while '$' not in product[0]:
        index = fake.pyint(min_value=0, max_value=len(category_list)-1)
        product = category_list[index]
        category_list.pop(index)
    return product[0], product[1], index
    
def get_random_item_from_category(category_list):
    price, product_name, index = get_random_product_from_csv(category_list)
    return Item(name=str(product_name),
                count=fake.pyint(min_value=1, max_value=5),
                unit_price=float(price.replace('$', '').replace(',', '')),
                tax=10), index


def generate_invoices(number):
    for i in range(number):
        start_date, end_date = get_random_invoice_dates()
        invoice = Invoice(get_random_client(), get_random_provider(), fake.pyint(min_value=10000000, max_value=99999999),
                          start_date, end_date, fake.city())
        category = get_random_category()
        with open(PATH_TO_DATA_SOURCES + category +'.csv', newline='', encoding="utf8") as csvfile:
            category_list = list(csv.reader(csvfile, delimiter=','))
            for _ in range(fake.pyint(min_value=1, max_value=7)):
                item, _ = get_random_item_from_category(category_list)
                # category_list.pop(index) check this
                invoice.add_item(item)
            SimpleInvoice(invoice, PATH_TO_GENERATED_INVOICES + 'invoice_'+str(i)+'.pdf', 'en')


if __name__ == "__main__":
    generate_invoices(1000)
