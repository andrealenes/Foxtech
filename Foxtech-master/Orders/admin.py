from django.contrib import admin
from .models import TypeOfDelivery
from .models import TypeAccountingDocument
from .models import PaymentType
from .models import Order
from .models import AccountingDocument
from .models import Address

@admin.register(AccountingDocument)
class AccountingDocumentAdmin(admin.ModelAdmin):
    list_display = ['id_accounting_document', 'number_accounting_document', 'accounting_document_date', 'order']
    list_per_page = 12

    fieldsets = (
        (None, {
            'fields': ('order',)
        }),
    )

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['id_address', 'user', 'default', 'city', 'modified']
    search_fields = ['user', 'address', 'user']
    list_filter = ['city', 'user']
    list_per_page = 12


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['identifier', 'order_date', 'state', 'user', 'total', 'address', 'send_bill']

    fieldsets = (
        (None, {
            'fields': ('type_of_delivery', 'type_accounting_document', 'payment_type', 'user', 'state', 'cart', 'total', 'shipping_total', 'address', )
        }),
    )

@admin.register(TypeOfDelivery) 
class TypeOfDeliveryAdmin(admin.ModelAdmin):
    list_display = ["description"]
    list_display_links = ["description"] 
    search_fields = ["description"] 
    list_per_page = 12


@admin.register(TypeAccountingDocument) 
class TypeAccountingDocumentAdmin(admin.ModelAdmin):
    list_display = ["nature"]
    list_display_links = ["nature"] 
    search_fields = ["nature"] 
    list_per_page = 12

@admin.register(PaymentType) 
class PaymentTypeAdmin(admin.ModelAdmin):
    list_display = ["description"]
    list_display_links = ["description"] 
    search_fields = ["description"] 
    list_per_page = 12