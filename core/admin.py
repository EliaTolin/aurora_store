from django.contrib import admin
from .models import App, OrderApp, Order, BillingAddress, Payment


class AppModelAdmin(admin.ModelAdmin):
    model = App
    list_display = ["name", "price", "category",
                    "device", "email", "app_id"]
    search_fields = ["name", "category", "email",
                     "developer", "data", "app_id"]
    list_filter = ["category", "email",
                   "developer", "data", "app_id"]


admin.site.register(App, AppModelAdmin)
admin.site.register(OrderApp)
admin.site.register(Order)
admin.site.register(BillingAddress)
admin.site.register(Payment)
