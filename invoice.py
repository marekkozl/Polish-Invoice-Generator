# -*- coding: utf-8 -*-

from InvoiceGenerator.api import Invoice, Item, Client, Provider
from InvoiceGenerator.pdf import SimpleInvoice

import locale
locale.setlocale(locale.LC_ALL, '')

client = Client(name=u"Polidea Sp. z o.o.",
                address=u"Hoża 76/78",
                zip="00-682",
                city=u"Warszawa",
                nip="7010185832")

provider = Provider(name=u"Polidea Sp. z o.o.",
                    address=u"Hoża 76/78",
                    zip="00-682",
                    city=u"Warszawa",
                    nip="7010185832",
                    bank_name="Bank",
                    bank_account="11222233334444555566667777")

invoice_number = 1/1/2015

invoice = Invoice(client, provider)
invoice.add_item(Item(name=u"Usługa programistyczna",
                      count=1,
                      unit_price=1000,
                      tax=23))
invoice.add_item(Item(name=u"Usługa programistyczna 2",
                      count=1,
                      unit_price=1500,
                      tax=8))
invoice.add_item(Item(name=u"Usługa programistyczna 3",
                      count=1,
                      unit_price=12454,
                      tax=23))

pdf = SimpleInvoice(invoice, 'invoice.pdf')
