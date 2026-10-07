from django.contrib import admin

from .models import Account, Destination


class DestinationInline(admin.TabularInline):
    model = Destination
    extra = 0


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("account_name", "email", "account_id", "token_prefix")
    search_fields = ("account_name", "email", "account_id")
    readonly_fields = ("account_id", "token_prefix", "token_hash")
    inlines = (DestinationInline,)


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ("account", "url", "http_method")
    list_filter = ("http_method",)
