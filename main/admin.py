from django.contrib import admin
from .models import TelegramUser, Transaction, Catalog, Product, TelegramAccount, Order, ProductContent


class ProductContentAdminInline(admin.TabularInline):
    model = ProductContent

    def get_extra(self, request, obj=None, **kwargs):
        extra = 1
        return extra


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_filter = ('is_confirmed',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = (ProductContentAdminInline,)


@admin.register(TelegramAccount)
class TelegramAccountAdmin(admin.ModelAdmin):
    list_filter = ('is_banned',)
    list_display = ('__str__', 'balance', 'is_banned',)


admin.site.register(TelegramUser)
admin.site.register(Catalog)
admin.site.register(Order)
