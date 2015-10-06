# -*- coding: utf-8 -*-

from conf import _

__all__ = ['Client', 'Provider', 'Creator', 'Item', 'Invoice']


class UnicodeProperty(object):
    _attrs = ()

    def __setattr__(self, key, value):
        if key in self._attrs:
            value = unicode(value)
        self.__dict__[key] = value


class Address(UnicodeProperty):
    _attrs = ('name', 'address1', 'address2', 'country', 'bank_data', 'bank_account', 'payment_terms', 'nip', 'echange_rate')

    def __init__(self, name, address1='', address2='', country='', bank_data='', bank_account='', payment_terms='', nip='', exchange_rate=''):
        self.name = name
        self.address1 = address1
        self.address2 = address2
        self.country = country
        self.nip = nip
        self.bank_data = bank_data
        self.bank_account = bank_account
        self.payment_terms = payment_terms
        self.exchange_rate = exchange_rate


class Client(Address):
    pass


class Provider(Address):
    pass


class Item(object):

    def __init__(self, name, count, unit_price, tax, unit=_("szt.")):
        self._count = float(count)
        self._unit_price = float(unit_price)
        self._name = unicode(name)
        self._unit = unicode(unit)
        self._tax = float(tax)

    @property
    def total_net_price(self):
        return self.unit_price * self.count

    @property
    def total_tax(self):
        return self.total_net_price * (1.0 + self.tax / 100.0)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = unicode(value)

    @property
    def count(self):
        return self._count

    @count.setter
    def count(self, value):
        try:
            self._count = float(value)
        except TypeError:
            self._count = 0

    @property
    def unit_price(self):
        return self._unit_price

    @unit_price.setter
    def unit_price(self, value):
        try:
            self._unit_price = float(value)
        except TypeError:
            self._unit_price = 0.0

    @property
    def unit(self):
        return self._unit

    @unit.setter
    def unit(self, value):
        self._unit = unicode(value)

    @property
    def tax(self):
        return self._tax

    @tax.setter
    def tax(self, value):
        try:
            self._tax = float(value)
        except TypeError:
            self._tax = 0.0


class GroupedItem(object):
    def __init__(self, vat):
        self.net = 0
        self.vat = float(vat)

    @property
    def tax(self):
        return self.net * (self.vat / 100)

    @property
    def gross(self):
        return self.net * ((100 + self.vat) / 100)

class Invoice(UnicodeProperty):
    _attrs = ('title', 'variable_symbol', 'specific_symbol', 'pay_type',
              'currency', 'currency_locale')

    rounding_result = False

    def __init__(self, client, provider, invoice_number, invoice_date, invoice_place, currency_string='zł ', notes=''):
        assert isinstance(client, Client)
        assert isinstance(provider, Provider)

        self.client = client
        self.provider = provider
        self._items = []
        self.date = None
        self.payback = None
        self.taxable_date = None
        self.invoice_number = invoice_number
        self.invoice_date = invoice_date
        self.invoice_place = invoice_place
        self.currency_string = currency_string
        self.notes = notes

        for attr in self._attrs:
            self.__setattr__(attr, '')

    @property
    def price(self):
        return self._round_result(sum([item.total for item in self.items]))

    @property
    def price_tax(self):
        return self._round_result(sum([item.total_tax for item in self.items]))

    def add_item(self, item):
        assert isinstance(item, Item)
        self._items.append(item)

    @property
    def items(self):
        return self._items

    @property
    def use_tax(self):
        use_tax = False
        for item in self.items:
            if item.tax:
                use_tax = True
                continue
        return use_tax

    @property
    def difference_in_rounding(self):
        price = sum([item.total_tax for item in self.items])
        return round(price, 0) - price

    def _get_grouped_items_by_tax(self):
        table = {}
        for item in self.items:
            if item.tax not in table:
                table[item.tax] = GroupedItem(item.tax)

            table[item.tax].net += item.total_net_price

        return table

    def items_summary(self):
        summary = {"net": 0, "tax": 0, "gross": 0}
        grouped_item = self._get_grouped_items_by_tax()
        for item in grouped_item.itervalues():
            summary["net"] += item.net
            summary["tax"] += item.tax
            summary["gross"] += item.gross
        return summary

    def _round_result(self, price):
        if self.rounding_result:
            price = round(price, 0)
        return price

    def generate_breakdown_vat(self):
        return self._get_grouped_items_by_tax()

    def generate_breakdown_vat_table(self):
        rows = []
        for vat,items in self.generate_breakdown_vat().iteritems():
             rows.append((vat, items['total'], items['total_tax'], items['tax']))

        return rows

