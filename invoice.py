# -*- coding: utf-8 -*-

from InvoiceGenerator.api import Invoice, Item, Client, Provider
from InvoiceGenerator.pdf import SimpleInvoice

import locale
locale.setlocale(locale.LC_ALL, '')

client = Client(name=u"Polidea Sp. z o.o.",
                address1=u"Hoża 76/78",
                address2=u"00-682 Warszawa",
                nip="7010185832")

provider = Provider(name=u"Polidea Sp. z o.o.",
                    address1=u"Hoża 76/78",
                    address2=u"00-682 Warszawa",
                    nip="7010185832",
                    bank_name="Bank",
                    bank_account="11222233334444555566667777")

invoice_number = u"1/1/2015"
invoice_date = u"23.01.2015"

invoice = Invoice(client, provider, invoice_number, invoice_date)
invoice.add_item(Item(name=u"Usługa programistyczna\nusługa B która będzie bardzo długa",
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
