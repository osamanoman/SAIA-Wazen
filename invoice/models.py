from django.db import models
from django.utils.translation import gettext_lazy as _

from product.models import Product
from company.models import Company
from datetime import date

# Create your models here.


class Invoice(models.Model):
    number = models.IntegerField(_("Invoice No."))
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    price = models.FloatField(_("Invoice Price"))
    issue_date = models.DateField(_("Issue Date"))
    print_date = models.DateField(_("Print Date"), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.number)


class InvoiceDetails(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.FloatField(_("Quantity"))
    product_price = models.FloatField(_("Product price"))
    discount_percentage = models.FloatField(_("Discount percentage"), max_length=100, default=0.0)
    total_without_tax = models.FloatField(_("Total without tax"))
    tax_price = models.FloatField(_("Tax Price"))
    total_with_tax = models.FloatField(_("Total with tax"))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.invoice)

    class Meta:
        verbose_name = _('Invoice Detail')
        verbose_name_plural = _('Invoice Details')


class Transaction(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.FloatField(_("Price"))
    transaction_date = models.DateField(_("Transaction Date"))
