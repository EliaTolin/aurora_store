from autoslug import AutoSlugField
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

from core.model_enums import AppCategories, Devices


'''App model'''


class App(models.Model):

    name = models.CharField(max_length=100,)
    description = models.TextField(max_length=1000)
    image = models.ImageField()
    price = models.FloatField(validators=[MinValueValidator(0.0)], default=0)
    category = models.CharField(choices=AppCategories.choices, max_length=20)
    app_id = models.CharField(max_length=40)
    version = models.CharField(max_length=40, default="1.0.0")
    slug = AutoSlugField(populate_from='app_id',
                         unique=True)
    device = models.CharField(choices=Devices.choices, max_length=20)
    developer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="app")
    data = models.DateTimeField(auto_now_add=True)
    ordered = models.BooleanField(default=False)
    sales_count = models.IntegerField(default=0)
    email = models.EmailField(max_length=100)
    raiting = models.FloatField(default=0, validators=[
                                MinValueValidator(0.0), MaxValueValidator(5.0)],)
    total_rate = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("app_view", kwargs={"slug": self.slug})

    def show_app(self):
        return reverse("user_app_view", kwargs={"slug": self.slug})

    def get_add_to_cart_url(self):
        return reverse('add_to_cart', kwargs={'slug': self.slug})

    def get_remove_from_cart_url(self):
        return reverse('remove_from_cart', kwargs={'slug': self.slug})

    def get_device_label(self):
        return Devices._value2member_map_[self.device].label

    def is_for_android(self):
        return self.device == Devices.android.name

    def is_for_ios(self):
        return self.device == Devices.ios.name

    def get_category_display(self):
        return AppCategories._value2member_map_[self.category].label


'''Model for relation from App and Order'''


class OrderApp(models.Model):
    product = models.ForeignKey(App, on_delete=models.CASCADE, null=True)
    is_valutated = models.BooleanField(default=False)
    is_ordered = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    ordered_date = models.DateTimeField(default=timezone.now)
    recommended = models.BooleanField(default=False)

    def __str__(self):
        return self.product.name

    def get_tot_price(self):
        return self.product.price

    def get_final_price(self):
        return self.get_tot_price()

    class Meta:
        verbose_name_plural = 'Order Apps'


'''Order model using for track an order with multiple OrderApp'''


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    is_ordered = models.BooleanField(default=False)
    apps = models.ManyToManyField(OrderApp)
    ordered_date = models.DateTimeField()
    billing_address = models.ForeignKey(
        'BillingAddress', on_delete=models.SET_NULL, blank=True, null=True)

    def get_total(self):
        total = 0
        for order_app in self.apps.all():
            total += order_app.get_tot_price()
        return total

    def do_checkout(self):
        return len(self.apps.all()) > 0

    def __str__(self):
        return self.user.username

    def get_username(self):
        return self.user.username

    def get_address(self):
        return self.billing_address.city + " " + self.billing_address.route


'''Billing address model'''


class BillingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    country = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    cap = models.CharField(max_length=5)
    route = models.CharField(max_length=50)
    house_number = models.CharField(max_length=30, blank=True)
    note = models.TextField(blank=True)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username
