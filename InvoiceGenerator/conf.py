# -*- coding: utf-8 -*-

APP_NAME = "InvoiceGenerator"

FONT_PATH = '/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans.ttf'
FONT_BOLD_PATH = '/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans-Bold.ttf'

lang = 'pl'

def _(message):
    if lang == 'pl':
        return message
    else:
        t = pl_2_plen.get(message)
        if t == None:
            print 'No translation for text: '+message
        else:
            if t=='':
                return message
        return t

pl_2_plen = {
    "szt.":'szt./each',
    "strona %(page_number)d z %(page_count)d":'strona %(page_number)d z %(page_count)d/page %(page_number)d out of %(page_count)d',
    "Wystawiono dnia:":'Wystawiono dnia/Date of issue:',
    "Miejsce wystawienia:":'Miejsce wystawienia/Place of issue:',
    "Faktura VAT nr: {}":'Faktura VAT nr/Invoice no: {}',
    "Data wykonania usługi:":'Data wykonania usługi/Date of shipment:',
    "Sposób zapłaty:":'',
    "Sprzedawca:":'Sprzedawca/Seller:',
    "Nabywca:":'Nabywca/Client:',
    "NIP: %(nip)s":'NIP/Tax Id: %(nip)s',
    "POZYCJE FAKTURY":'POZYCJE FAKTURY/ITEMS',
    "Lp.":'Lp.<br/>No.',
    "Nazwa towaru lub usługi":'Nazwa towaru lub usługi<br/>Description',
    "Ilość":'Ilość<br/>Qty',
    "Jedn.":'Jedn.<br/>UM',
    "Cena jedn. netto":'Cena jedn. netto<br/>Net price',
    "Wartość netto":'Wartość netto<br/>Net worth',
    "Stawka VAT":'Stawka VAT<br/>VAT [%]',
    "Wartość brutto":'Wartość brutto<br/>Gross worth',
    "PODSUMOWANIE":'PODSUMOWANIE/SUMMARY',
    "VAT":'VAT',
    "Razem:":'Razem/Total',
    "Termin płatności:":'Termin płatności/Payment terms:',
    "Konto bankowe:":'Konto bankowe/Bank account:',
    "Bank:":'Bank:',
    "Kurs NBP:":'Kurs NBP/Official exchange rate:'
}
