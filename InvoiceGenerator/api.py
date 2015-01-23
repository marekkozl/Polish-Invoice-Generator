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
    _attrs = ('name', 'address1', 'address2', 'bank_name', 'bank_account', 'nip')

    def __init__(self, name, address1='', address2='', bank_name='', bank_account='', nip=''):
        self.name = name
        self.address1 = address1
        self.address2 = address2
        self.nip = nip
        self.bank_name = bank_name
        self.bank_account = bank_account

    @property
    def account_info(self):
        return "{} {} {} {} {} {} {} {}".format(self.bank_name,
                                                self.bank_account[0:2],
                                                self.bank_account[2:6],
                                                self.bank_account[6:10],
                                                self.bank_account[10:14],
                                                self.bank_account[14:18],
                                                self.bank_account[18:22],
                                                self.bank_account[22:26])


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
              'currency', 'currency_locale', 'number')

    rounding_result = False

    def __init__(self, client, provider):
        assert isinstance(client, Client)
        assert isinstance(provider, Provider)

        self.client = client
        self.provider = provider
        self._items = []
        self.date = None
        self.payback = None
        self.taxable_date = None
        self.grouped_values = {}

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
            if not table.has_key(item.tax):
                table[item.tax] = {'total': item.total, 'total_tax': item.total_tax, 'tax': item.count_tax()}
            else:
                table[item.tax]['total'] += item.total
                table[item.tax]['total_tax'] +=  item.total_tax
                table[item.tax]['tax'] +=  item.count_tax()

        return table

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

