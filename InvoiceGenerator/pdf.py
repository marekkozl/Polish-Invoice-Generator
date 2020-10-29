# -*- coding: utf-8 -*-

import locale
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.enums import *

from conf import _, FONT_PATH, FONT_BOLD_PATH
import conf
from api import Invoice


def format_amount(amount):
    return "{:,.2f}".format(amount).replace(",", " ").replace(".", ",")


class BaseInvoice(object):

    def __init__(self, invoice):
        # assert isinstance(invoice, Invoice)

        self.invoice = invoice
        self.pdf = None

    def gen(self):
        pass


class NumberedCanvas(Canvas):
    def __init__(self, *args, **kwargs):
        Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            if num_pages > 1:
                self.draw_page_number(num_pages)
            Canvas.showPage(self)
        Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont("DejaVu", 9)
        self.drawRightString(self._pagesize[0] - 15*mm, 6*mm,
            _("strona %(page_number)d z %(page_count)d") % {"page_number": self._pageNumber, "page_count": page_count})


from gettext import NullTranslations

class SimpleInvoice(BaseInvoice):

    def __init__(self, invoice, filename, language=''):
        if language == 'en':
            conf.lang = 'en'
        else:
            conf.lang = 'pl'

        super(SimpleInvoice, self).__init__(invoice)

        self.pageSize = A4
        self.width = self.pageSize[0]
        self.height = self.pageSize[1]

        self.top = self.height - 13 * mm
        self.left = 17 * mm
        self.right = self.width - self.left

        self.normalFontSize = 10
        self.smallFontSize = 9
        self.tinyFontSize = 8
        self.largeFontSize = 12
        self.bigFontSize = 11

        self.fillDarkColor = (0.8, 0.8, 0.8)
        self.fillLightColor = (0.9, 0.9, 0.9)
        self.textColor = (0, 0, 0)

        pdfmetrics.registerFont(TTFont('DejaVu', FONT_PATH))
        pdfmetrics.registerFont(TTFont('DejaVu-Bold', FONT_BOLD_PATH))

        self.pdf = NumberedCanvas(filename, pagesize=self.pageSize)

        self.pdf.setStrokeColor(self.textColor)
        self.gen()

    def gen(self):
        self.drawHeaders()

        company_data_top = self.height - 60 * mm
        seller_bottom = self.drawSeller(company_data_top)
        self.drawPurchaser(company_data_top)
        items_bottom = self.drawInvoiceItems(seller_bottom - 10 * mm)
        self.drawSummary(items_bottom - 10 * mm)

        self.drawRightSideRect()

        self.pdf.showPage()
        self.pdf.save()

    #############################################################
    ## New draw methods
    #############################################################

    def drawRightSideRect(self):
        self.pdf.setFillColor(self.fillDarkColor)
        width = 4 * mm
        self.pdf.rect(self.right + 4 * mm, 0, width, self.height, stroke=False, fill=True)
        self.pdf.setFillColor(self.textColor)

    def drawLeftSideRect(self, y):
        self.pdf.setFillColor(self.fillDarkColor)
        height = 3 * mm
        self.pdf.rect(0, y, self.left - 2 * mm, height, stroke=False, fill=True)
        self.pdf.setFillColor(self.textColor)

    def drawHeaders(self):
        self.headerLeft = self.width / 2
        padding = 1.5 * mm
        value_padding = 85 * mm
        invoice_number_string = _("Faktura VAT nr: {}").format(self.invoice.invoice_number)
        self.pdf.setFont('DejaVu-Bold', self.largeFontSize)
        bottom = self.top
        self.pdf.drawString(self.left, bottom, invoice_number_string)

        self.pdf.setFont('DejaVu', self.bigFontSize)
        bottom -= self.bigFontSize + padding*3
        self.pdf.drawString(self.left, bottom, _("Wystawiono dnia:"))

        date_string = self.invoice.invoice_issue_date
        self.pdf.drawString(self.left + value_padding, bottom, date_string)

        # if not self.invoice.invoice_date:
        #     invoice_date_string = _("Data wykonania usługi:")
        #     self.pdf.setFont('DejaVu', self.bigFontSize)
        #     bottom -= self.bigFontSize + padding
        #     self.pdf.drawString(self.left, bottom, invoice_date_string)
        #     invoice_date_value_string = self.invoice.invoice_date
        #     self.pdf.drawString(self.left + value_padding, bottom, invoice_date_value_string)

        # self.pdf.setFont('DejaVu', self.bigFontSize)
        # bottom -= self.bigFontSize + padding
        # self.pdf.drawString(self.left, bottom, _("Miejsce wystawienia:"))

        # place_string = self.invoice.invoice_place
        # self.pdf.drawString(self.left + value_padding, bottom, place_string)


    def drawSeller(self, top):
        self.pdf.setFont('DejaVu-Bold', self.largeFontSize)
        padding_left = 1 * mm
        bottom = top
        self.pdf.drawString(self.left, bottom, _("Sprzedawca:"))

        self.drawLeftSideRect(bottom)

        seller_name_string = self.invoice.provider.name
        self.pdf.setFont('DejaVu', self.normalFontSize)
        bottom -= self.normalFontSize + 4 * mm
        self.pdf.drawString(self.left + padding_left, bottom, seller_name_string)

        seller_address_string = self.invoice.provider.address1
        bottom -= self.normalFontSize + mm
        self.pdf.drawString(self.left + padding_left, bottom, seller_address_string)

        seller_code_string = self.invoice.provider.address2
        bottom -= self.normalFontSize + mm
        self.pdf.drawString(self.left + padding_left, bottom, seller_code_string)

        provider_country_string = self.invoice.provider.country
        bottom -= self.normalFontSize + mm
        self.pdf.drawString(self.left + padding_left, bottom, provider_country_string)

        if self.invoice.provider.nip and self.invoice.provider.nip.strip():
            seller_nip_string = _('NIP: %(nip)s') % {"nip": self.invoice.provider.nip}
            bottom -= self.normalFontSize + mm
            self.pdf.drawString(self.left + padding_left, bottom, seller_nip_string)

        return bottom

    def drawPurchaser(self, top):
        self.pdf.setFont('DejaVu-Bold', self.largeFontSize)
        padding_left = 1 * mm
        bottom = top
        self.pdf.drawString(self.headerLeft, bottom, _("Nabywca:"))

        purchaser_name_string = self.invoice.client.name
        self.pdf.setFont('DejaVu', self.normalFontSize)
        bottom -= self.normalFontSize + 4 * mm
        self.pdf.drawString(self.headerLeft + padding_left, bottom, purchaser_name_string)

        purchaser_address_string = self.invoice.client.address1
        bottom -= self.normalFontSize + mm
        self.pdf.drawString(self.headerLeft + padding_left, bottom, purchaser_address_string)

        purchaser_code_string = self.invoice.client.address2
        bottom -= self.normalFontSize + mm
        self.pdf.drawString(self.headerLeft + padding_left, bottom, purchaser_code_string)

        purchaser_country_string = self.invoice.client.country
        bottom -= self.normalFontSize + mm
        self.pdf.drawString(self.headerLeft + padding_left, bottom, purchaser_country_string)

        if self.invoice.client.nip and self.invoice.client.nip.strip():
            purchaser_nip_string = _('NIP: %(nip)s') % {"nip": self.invoice.client.nip}
            bottom -= self.normalFontSize + mm
            self.pdf.drawString(self.headerLeft + padding_left, bottom, purchaser_nip_string)

        return bottom

    def drawInvoiceItems(self, y):
        self.pdf.setFont('DejaVu-Bold', self.largeFontSize)
        self.pdf.drawString(self.left, y, _("POZYCJE FAKTURY"))

        self.drawLeftSideRect(y)

        table_top = y - 5 * mm
        table_width = self.right - self.left
        cell_padding = 2 * mm
        column_padding = 3.5 * mm
        self.pdf.setFont('DejaVu-Bold', self.normalFontSize)

        lp_max_width = 8 * mm
        lp_left = self.left + cell_padding

        name_max_width = 46 * mm
        name_left = lp_left + lp_max_width + column_padding

        quantity_max_width = 12 * mm
        quantity_left = name_left + name_max_width + column_padding

        unit_max_width = 12 * mm
        unit_left = quantity_left + quantity_max_width + column_padding

        unit_price_net_max_width = 18 * mm
        unit_price_net_left = unit_left + unit_max_width + column_padding

        price_net_max_width = 18 * mm
        price_net_left = unit_price_net_left + unit_price_net_max_width + column_padding

        vat_max_width = 15 * mm
        vat_left = price_net_left + price_net_max_width + column_padding

        price_gross_max_width = 18 * mm
        price_gross_left = vat_left + vat_max_width + column_padding

        center_style = ParagraphStyle('normal', fontName='DejaVu-Bold', fontSize=self.tinyFontSize,
                                      alignment=TA_CENTER, leading=10)
        left_style = ParagraphStyle('normal', fontName='DejaVu-Bold', fontSize=self.tinyFontSize, alignment=TA_LEFT,
                                    leading=10)
        right_style = ParagraphStyle('normal', fontName='DejaVu-Bold', fontSize=self.tinyFontSize, alignment=TA_RIGHT,
                                     leading=10)
        header_max_height = 0

        par = Paragraph(_("Lp."), center_style)
        par_width, par_height = par.wrapOn(self.pdf, lp_max_width, 0)
        header_max_height = max(header_max_height, par_height)
        par.drawOn(self.pdf, lp_left, table_top - (cell_padding + par_height))

        par = Paragraph(_("Nazwa towaru lub usługi"), left_style)
        par_width, par_height = par.wrapOn(self.pdf, name_max_width, 0)
        header_max_height = max(header_max_height, par_height)
        par.drawOn(self.pdf, name_left, table_top - (cell_padding + par_height))

        par = Paragraph(_("Ilość"), right_style)
        par_width, par_height = par.wrapOn(self.pdf, quantity_max_width, 0)
        header_max_height = max(header_max_height, par_height)
        par.drawOn(self.pdf, quantity_left, table_top - (cell_padding + par_height))

        par = Paragraph(_("Jedn."), center_style)
        par_width, par_height = par.wrapOn(self.pdf, unit_max_width, 0)
        header_max_height = max(header_max_height, par_height)
        par.drawOn(self.pdf, unit_left, table_top - (cell_padding + par_height))

        par = Paragraph(_("Cena jedn. netto"), right_style)
        par_width, par_height = par.wrapOn(self.pdf, unit_price_net_max_width, 0)
        header_max_height = max(header_max_height, par_height)
        par.drawOn(self.pdf, unit_price_net_left, table_top - (cell_padding + par_height))

        par = Paragraph(_("Wartość netto"), right_style)
        par_width, par_height = par.wrapOn(self.pdf, price_net_max_width, 0)
        header_max_height = max(header_max_height, par_height)
        par.drawOn(self.pdf, price_net_left, table_top - (cell_padding + par_height))

        par = Paragraph(_("Stawka VAT"), right_style)
        par_width, par_height = par.wrapOn(self.pdf, vat_max_width, 0)
        header_max_height = max(header_max_height, par_height)
        par.drawOn(self.pdf, vat_left, table_top - (cell_padding + par_height))

        par = Paragraph(_("Wartość brutto"), right_style)
        par_width, par_height = par.wrapOn(self.pdf, price_gross_max_width, 0)
        header_max_height = max(header_max_height, par_height)
        par.drawOn(self.pdf, price_gross_left, table_top - (cell_padding + par_height))

        self.pdf.setStrokeColor(self.fillDarkColor)
        row_height = header_max_height + 2 * cell_padding
        self.pdf.rect(self.left, table_top - row_height, table_width, row_height)

        center_style = ParagraphStyle('normal', fontName='DejaVu', fontSize=self.tinyFontSize,
                                      alignment=TA_CENTER, leading=10)
        left_style = ParagraphStyle('normal', fontName='DejaVu', fontSize=self.tinyFontSize, alignment=TA_LEFT,
                                    leading=10)
        right_style = ParagraphStyle('normal', fontName='DejaVu', fontSize=self.tinyFontSize, alignment=TA_RIGHT,
                                     leading=10)

        row_top = table_top - row_height

        idx = 1
        for item in self.invoice.items:

            name_height = 0
            lines = item.name.split("\n")

            for line in lines:
                par = Paragraph(line, left_style)
                par_width, par_height = par.wrapOn(self.pdf, name_max_width, 0)
                name_height += par_height

            if idx % 2 == 1:
                self.pdf.setFillColor(self.fillLightColor)
            else:
                self.pdf.setFillColorRGB(1, 1, 1)

            row_height = name_height + 2 * cell_padding
            self.pdf.rect(self.left, row_top - row_height, table_width, row_height, fill=1)

            name_height = 0
            for line in lines:
                par = Paragraph(line, left_style)
                par_width, par_height = par.wrapOn(self.pdf, name_max_width, 0)
                name_height += par_height
                par.drawOn(self.pdf, name_left, row_top - (cell_padding + name_height))

            par = Paragraph("%d." % idx, center_style)
            par_width, par_height = par.wrapOn(self.pdf, lp_max_width, 0)
            par.drawOn(self.pdf, lp_left, row_top - (cell_padding + par_height))

            par = Paragraph(format_amount(item.count), right_style)
            par_width, par_height = par.wrapOn(self.pdf, quantity_max_width, 0)
            name_height += par_height
            par.drawOn(self.pdf, quantity_left, row_top - (cell_padding + par_height))

            par = Paragraph(item.unit, center_style)
            par_width, par_height = par.wrapOn(self.pdf, unit_max_width, 0)
            par.drawOn(self.pdf, unit_left, row_top - (cell_padding + par_height))

            par = Paragraph(format_amount(item.unit_price), right_style)
            par_width, par_height = par.wrapOn(self.pdf, unit_price_net_max_width, 0)
            par.drawOn(self.pdf, unit_price_net_left, row_top - (cell_padding + par_height))

            par = Paragraph(format_amount(item.total_net_price), right_style)
            par_width, par_height = par.wrapOn(self.pdf, price_net_max_width, 0)
            par.drawOn(self.pdf, price_net_left, row_top - (cell_padding + par_height))

            if item.use_vat == False:
                 par = Paragraph(item.use_vat_txt, right_style)
            else:
                par = Paragraph("%d%%" % item.tax, right_style)
            par_width, par_height = par.wrapOn(self.pdf, vat_max_width, 0)
            par.drawOn(self.pdf, vat_left, row_top - (cell_padding + par_height))

            par = Paragraph(format_amount(item.total_tax), right_style)
            par_width, par_height = par.wrapOn(self.pdf, price_gross_max_width, 0)
            par.drawOn(self.pdf, price_gross_left, row_top - (cell_padding + par_height))

            row_top -= row_height
            idx += 1

        return row_top

    def drawSummary(self, y):
        self.pdf.setFillColor(self.textColor)
        self.pdf.setFont('DejaVu-Bold', self.largeFontSize)
        self.pdf.drawString(self.left, y, _("PODSUMOWANIE"))

        self.drawLeftSideRect(y)

        table_top = y - 5 * mm
        table_width = self.right - self.left
        cell_padding = 2 * mm
        column_padding = 3.5 * mm
        self.pdf.setFont('DejaVu-Bold', self.normalFontSize)

        title_max_width = 53 * mm
        title_left = self.left + cell_padding

        vat_max_width = 25 * mm
        vat_left = title_left + title_max_width + column_padding

        net_max_width = 30 * mm
        net_left = vat_left + vat_max_width + column_padding

        tax_max_width = 20 * mm
        tax_left = net_left + net_max_width + column_padding

        gross_max_width = 30 * mm
        gross_left = tax_left + tax_max_width + column_padding

        center_style = ParagraphStyle('normal', fontName='DejaVu-Bold', fontSize=self.tinyFontSize,
                                      alignment=TA_CENTER, leading=10)
        center_normal_style = ParagraphStyle('normal', fontName='DejaVu', fontSize=self.tinyFontSize,
                                      alignment=TA_CENTER, leading=10)
        right_style = ParagraphStyle('normal', fontName='DejaVu-Bold', fontSize=self.tinyFontSize, alignment=TA_RIGHT,
                                     leading=10)
        right_normal_style = ParagraphStyle('normal', fontName='DejaVu', fontSize=self.tinyFontSize,
                                            alignment=TA_RIGHT, leading=10)

        row_top = table_top
        row_idx = 0

        par = Paragraph(_("Stawka VAT"), center_style)
        par_width, par_height = par.wrapOn(self.pdf, vat_max_width, 0)
        par.drawOn(self.pdf, vat_left, row_top - (cell_padding + par_height))

        par = Paragraph(_("Wartość netto"), right_style)
        par_width, par_height = par.wrapOn(self.pdf, net_max_width, 0)
        par.drawOn(self.pdf, net_left, row_top - (cell_padding + par_height))

        par = Paragraph(_("VAT"), right_style)
        par_width, par_height = par.wrapOn(self.pdf, tax_max_width, 0)
        par.drawOn(self.pdf, tax_left, row_top - (cell_padding + par_height))

        par = Paragraph(_("Wartość brutto"), right_style)
        par_width, par_height = par.wrapOn(self.pdf, gross_max_width, 0)
        par.drawOn(self.pdf, gross_left, row_top - (cell_padding + par_height))

        row_height = par_height + 2 * cell_padding
        row_top -= row_height
        row_idx += 1

        for key, item in self.invoice.generate_breakdown_vat().items():
            if row_idx % 2 == 1:
                self.pdf.setFillColor(self.fillLightColor)
                self.pdf.rect(self.left, row_top - row_height, table_width, row_height, fill=1, stroke=0)

            if key == -1:
                par = Paragraph(item.vat_txt, center_normal_style)
            else:
                par = Paragraph("%d%%" % item.vat, center_normal_style)
            par_width, par_height = par.wrapOn(self.pdf, vat_max_width, 0)
            par.drawOn(self.pdf, vat_left, row_top - (cell_padding + par_height))

            par = Paragraph(format_amount(item.net), right_normal_style)
            par_width, par_height = par.wrapOn(self.pdf, net_max_width, 0)
            par.drawOn(self.pdf, net_left, row_top - (cell_padding + par_height))

            par = Paragraph(format_amount(item.tax), right_normal_style)
            par_width, par_height = par.wrapOn(self.pdf, tax_max_width, 0)
            par.drawOn(self.pdf, tax_left, row_top - (cell_padding + par_height))

            par = Paragraph(format_amount(item.gross), right_normal_style)
            par_width, par_height = par.wrapOn(self.pdf, gross_max_width, 0)
            par.drawOn(self.pdf, gross_left, row_top - (cell_padding + par_height))

            row_top -= row_height

            row_idx += 1

        if row_idx % 2 == 1:
            self.pdf.setFillColor(self.fillLightColor)
            self.pdf.rect(self.left, row_top - row_height, table_width, row_height, fill=1, stroke=0)

        summary_data = self.invoice.items_summary()

        par = Paragraph(_("Razem:"), right_style)
        par_width, par_height = par.wrapOn(self.pdf, title_max_width, 0)
        par.drawOn(self.pdf, title_left, row_top - (cell_padding + par_height))

        par = Paragraph(self.invoice.currency_string+format_amount(summary_data["net"]), right_style)
        par_width, par_height = par.wrapOn(self.pdf, net_max_width, 0)
        par.drawOn(self.pdf, net_left, row_top - (cell_padding + par_height))

        par = Paragraph(self.invoice.currency_string+format_amount(summary_data["tax"]), right_style)
        par_width, par_height = par.wrapOn(self.pdf, tax_max_width, 0)
        par.drawOn(self.pdf, tax_left, row_top - (cell_padding + par_height))

        par = Paragraph(self.invoice.currency_string+format_amount(summary_data["gross"]), right_style)
        par_width, par_height = par.wrapOn(self.pdf, gross_max_width, 0)
        par.drawOn(self.pdf, gross_left, row_top - (cell_padding + par_height))

        row_top -= row_height
        self.pdf.setStrokeColor(self.fillDarkColor)
        self.pdf.rect(self.left, row_top, table_width, table_top - row_top)

        row_top -= row_height

        value_padding = 85 * mm
        self.pdf.setStrokeColor(self.textColor)
        self.pdf.setFillColor(self.textColor)
        self.pdf.setFont('DejaVu', self.bigFontSize)

        if not self.invoice.provider.bank_account:
            row_top -= 1.5 * self.bigFontSize
            self.pdf.drawString(self.left, row_top, _("Konto bankowe:"))
            self.pdf.drawString(self.left + value_padding, row_top, self.invoice.provider.bank_account)

        if not self.invoice.provider.bank_data and self.invoice.provider.bank_data.strip():
            row_top -= 1.5 * self.bigFontSize
            self.pdf.drawString(self.left, row_top, _("Bank:"))
            self.pdf.drawString(self.left + value_padding, row_top, self.invoice.provider.bank_data)

        if not self.invoice.provider.payment_terms:
            row_top -= 1.5 * self.bigFontSize
            self.pdf.drawString(self.left, row_top, _("Termin płatności:"))
            self.pdf.drawString(self.left + value_padding, row_top, self.invoice.provider.payment_terms)

        if self.invoice.provider.exchange_rate.strip():
            row_top -= 1.5 * self.bigFontSize
            self.pdf.drawString(self.left, row_top, _("Kurs NBP:"))
            self.pdf.drawString(self.left + value_padding, row_top, self.invoice.provider.exchange_rate)

        if self.invoice.notes and self.invoice.notes.strip():
            row_top -= 1.5 * self.bigFontSize
            self.pdf.drawString(self.left, row_top, _("Uwagi:"))
            lines = self.invoice.notes.split("\n")

            for line in lines:
                self.pdf.drawString(self.left + value_padding, row_top, line)
                row_top -= 1.5 * self.bigFontSize
            
