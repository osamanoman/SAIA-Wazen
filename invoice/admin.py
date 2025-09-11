from django.contrib import admin

from .models import Invoice, InvoiceDetails, Transaction


# Register your models here.

class InlineInvoiceDetail(admin.TabularInline):
    model = InvoiceDetails
    extra = 1


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    inlines = [InlineInvoiceDetail, ]
    list_display = ('id', 'number', 'company', 'price', 'issue_date', 'created_date')
    search_fields = ('number', 'company__name__icontains', 'price', 'issue_date')

    def created_date(self, obj):
        return obj.created_at.strftime("%Y-%h-%d %H:%M:%S")


@admin.register(InvoiceDetails)
class InvoiceDetailsAdmin(admin.ModelAdmin):
    list_display = ('id', 'invoice', 'product', 'quantity', 'product_price', 'total_without_tax', 'total_with_tax',
                    'created_date')
    search_fields = ('invoice__number__icontains', 'product__name__icontains', 'total_without_tax', 'total_with_tax')

    def created_date(self, obj):
        return obj.created_at.strftime("%Y-%h-%d %H:%M:%S")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'price', 'transaction_date')
    search_fields = ('product__name__icontains', )

