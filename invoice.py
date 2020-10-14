# -*- coding: utf-8 -*-

from InvoiceGenerator.api import Invoice, Item, Client, Provider
from InvoiceGenerator.pdf import SimpleInvoice
from faker import Faker
import random
from datetime import datetime
from datetime import timedelta
import locale
locale.setlocale(locale.LC_ALL, '')

region = 'en_US'
fake = Faker(region)


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
                        bank_data="Bank",
                        bank_account=fake.pyint(min_value=10000000000000000000000000, max_value=99999999999999999999999999))
    return provider


def get_random_client():
    person = fake.profile()
    street, address = person.get('residence').split('\n')
    client = Client(name=person.get('company'),
                    address1=street,
                    address2=address,
                    nip=fake.itin())
    return client


def get_random_item_from_category(category):
    #todo
    return Item(name=u"Service",
                count=fake.pyint(min_value=1, max_value=100),
                unit_price=fake.pyint(min_value=100, max_value=1000),
                tax=23)


def generate_invoices(number):
    for _ in range(number):
        start_date, end_date = get_random_invoice_dates()
        invoice = Invoice(get_random_client(), get_random_provider(), fake.pyint(min_value=10000000, max_value=99999999),
                          start_date, end_date, fake.city())
        for _ in range(fake.pyint(min_value=1, max_value=7)):
            item = get_random_item_from_category('nil')
            invoice.add_item(item)
        SimpleInvoice(invoice, 'invoice_'+str(i)+'.pdf', 'en')


if __name__ == "__main__":
    generate_invoices(4)
