import datetime
import json
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, DeleteView, UpdateView
from django.views.generic.list import ListView

from accounts.models import UserProfile

from .forms import CheckoutForm, RaitingForm
from .models import App, Order, OrderApp, BillingAddress, Payment
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from core.model_enums import AppCategories, Devices


'''
View for show all apps in homepage
'''


class AllAppView(ListView):
    model = App
    paginate_by = 4
    template_name = 'core/app_page.html'
    queryset = App.objects.filter(ordered=False).order_by("-pk")


''' 
Recommender system
'''


def get_home_view(request):
    app_list = App.objects.all()
    recommendation_list = []
    iosconvenient_list = []
    androidconvenient_list = []

    user = None
    device_user = None
    if request.user.is_authenticated:
        user = UserProfile.objects.filter(user=request.user).first()
    if user:
        device_user = user.user_device

    for app in app_list:
        recommendation_list.append(app)
        if app.is_for_ios():
            iosconvenient_list.append(app)
        if app.is_for_android():
            androidconvenient_list.append(app)

    recommendation_list = sorted(recommendation_list, key=lambda app_el: (
        app_el.sales_count), reverse=True)
    ios_convenient_list = sorted(iosconvenient_list, key=lambda app_el: (
        app_el.raiting), reverse=True)
    android_convenient_list = sorted(androidconvenient_list, key=lambda app_el: (
        app_el.raiting), reverse=True)

    context = {
        "recommendation_list": recommendation_list[:4],
        "iosconvenient_list": ios_convenient_list[:4],
        "androidconvenient_list": android_convenient_list[:4]
    }

    if device_user:
        context["user_device"] = device_user

    return render(request, 'core/homepage.html', context)


'''
Show profile
@param username : username's user
return: the page of user
'''


def get_user_profile_view(request, username):
    if request.user.username != username:
        return get_other_profile_view(request, username)
    user = get_object_or_404(User, username=username)
    user_apps = App.objects.filter(
        developer=user.pk, ordered=False).order_by("-pk")
    paginator = Paginator(user_apps, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {"user": user, "user_apps": page_obj, "page_obj": page_obj}
    return render(request, 'core/profile.html', context)


'''
View for create and add apps
'''


class AddAppView(CreateView):
    model = App

    fields = ["name", "app_id", "version", "description",
              "image", "price", "category", "device", "email"]
    template_name = "core/add_app.html"

    def form_valid(self, form):
        form.instance.developer_id = self.request.user.pk
        return super(AddAppView, self).form_valid(form)

    def get_success_url(self):
        success_url = reverse_lazy("homepage")
        messages.info(self.request, "App creata correttamente!")
        return success_url


'''
View an app
'''


class UserAppDetailView(DetailView):
    model = App
    template_name = "core/app.html"


'''
Show other profiles
'''


def get_other_profile_view(request, username):
    user = get_object_or_404(User, username=username)
    user_apps = App.objects.filter(
        developer=user.pk, ordered=False).order_by("-pk")
    paginator = Paginator(user_apps, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {"user": user, "user_apps": page_obj, "page_obj": page_obj}
    return render(request, 'core/user_profile.html', context)


'''
View for delete app
'''


class AppDeleteView(DeleteView):
    model = App
    template_name = 'core/app_delete.html'

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        appid = self.kwargs['pk']
        app = get_object_or_404(App, id=appid)

        if user.id is not app.developer.id:
            messages.error(request, "Non puoi accedere a questa pagina!")
            return get_home_view(request)

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        appid = self.kwargs['pk']
        app = get_object_or_404(App, id=appid)
        user = get_object_or_404(User, username=app.developer)
        messages.info(self.request, "App eliminata correttamente!")
        return reverse_lazy('user_profile', kwargs={'username': user})


'''
View for modify app
'''


class AppModifyView(UpdateView):
    model = App
    fields = ('name', 'version', 'description', 'price',
              'category', 'device', 'email')
    template_name = 'core/app_modify.html'

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        appid = self.kwargs['pk']
        app = get_object_or_404(App, id=appid)

        if user.id is not app.developer.id:
            messages.error(request, "Non puoi accedere a questa pagina!")
            return get_home_view(request)

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        appid = self.kwargs['pk']
        app = get_object_or_404(App, id=appid)
        user = get_object_or_404(User, username=app.developer)
        messages.info(self.request, "App modificata correttamente!")
        return reverse_lazy('user_profile', kwargs={'username': user})


'''View for raiting app'''


class AppRaitingView(UpdateView):
    model = App
    fields = ['raiting']
    template_name = 'core/app_raiting.html'

    def post(self, request, *args, **kwargs):
        form = RaitingForm(self.request.POST or None)
        if form.is_valid():
            rate = form.cleaned_data['raiting']
            if rate != 0:
                user_id = self.request.user.id
                user = User.objects.get(id=user_id)
                user_purchases = Payment.objects.filter(
                    user=user).order_by("-pk")
                for purchases in user_purchases:
                    order = Order.objects.get(
                        id=purchases.order.id, is_ordered=True)
                    for app in order.apps.all():
                        if app.product.id == self.kwargs['pk']:
                            app.is_valutated = True
                            app.product.total_rate += 1
                            if app.product.raiting == 0:
                                app.product.raiting = rate
                            else:
                                tmp = app.product.raiting * app.product.total_rate
                                tmp += rate
                                avg = tmp / app.product.total_rate
                                app.product.raiting = round(avg, 1)
                            app.product.save()
                            app.save()
                            messages.info(
                                request, "L'app è stata valutata correttamente")
                            return redirect('homepage')
        messages.warning(
            request, "Inserisci una valutazione corretta.")
        return redirect('app_rate', *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('product', kwargs={'slug': self.app.slug})


'''Function for add to cart the apps'''


def add_to_cart(request, slug):
    app = get_object_or_404(App, slug=slug)
    order_app, created = OrderApp.objects.get_or_create(
        product=app, user=request.user, is_ordered=False)
    order_qs = Order.objects.filter(user=request.user, is_ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.apps.filter(product__slug=app.slug).exists():
            order_app.save()
            messages.info(request, "Hai gia aggiunto questa app al carrello!")
        else:
            order.apps.add(order_app)
            messages.info(
                request, "L'app è stato aggiunta con successo al carrello")
            return redirect('homepage')
    else:
        date_ordered = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=date_ordered)
        order.apps.add(order_app)
        messages.info(
            request, "L' app è stato aggiunta con successo al carrello")

    return redirect('homepage')


'''Function for remove app from cart'''


def remove_from_cart(request, slug):
    app = get_object_or_404(App, slug=slug)
    order_qs = Order.objects.filter(user=request.user, is_ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.apps.filter(product__slug=app.slug).exists():
            order_app = OrderApp.objects.filter(
                product=app, user=request.user, is_ordered=False)[0]
            order.apps.remove(order_app)
            messages.info(
                request, "L'app è stato rimossa correttamente dal carrello")
            return redirect(reverse_lazy('order_summary'))
        else:
            messages.warning(request, "L' app non è nel carrello")
            return redirect(reverse_lazy('app_view', kwargs={'slug': slug}))
    else:
        messages.error(request, "Non hai un ordine attivo")
        return redirect(reverse_lazy('app_view', kwargs={'slug': slug}))


'''
This function check all field in the form for check is all not empties
'''


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


'''Order summary view'''


class OrderSummaryView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, is_ordered=False)
            context = {'object': order}
            return render(self.request, 'core/order/order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "Il carrello è vuoto")
            return redirect('homepage')


'''Checkout view'''


class CheckoutView(View):
    def get(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        context = {'form': form}

        billing_address_qs = BillingAddress.objects.filter(
            user=self.request.user, default=True)
        if billing_address_qs.exists():
            context.update(
                {'default_billing_address': billing_address_qs[0]})
        return render(self.request, 'core/order/checkout.html', context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, is_ordered=False)
            if form.is_valid():
                form.use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if form.use_default_shipping:
                    address_qs = BillingAddress.objects.filter(
                        user=self.request.user, default=True)
                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order_apps = order.apps.all()
                        order_apps.update(is_ordered=True)
                        order.billing_address = billing_address
                        for app in order_apps:
                            app.product.ordered = True
                            app.product.indirizzo = order.get_address()
                            app.product.data = timezone.now()
                            app.product.save()
                            app.save()

                        order.billing_address = billing_address
                        order.is_ordered = True
                        order.ordered_date = timezone.now()
                        order.save()
                        payment = Payment()
                        payment.user = self.request.user
                        payment.amount = order.get_total()
                        payment.order = order
                        payment.save()
                    else:
                        messages.info(
                            self.request, "Nessun indirizzo di default")
                        return redirect('checkout')
                else:
                    form.country = form.cleaned_data.get('country')
                    form.city = form.cleaned_data.get('city')
                    form.route = form.cleaned_data.get('route')
                    form.cap = form.cleaned_data.get('cap')
                    form.house_number = form.cleaned_data.get('house_number')
                    form.note = form.cleaned_data.get('note')

                    form.opzioni_pagamento = form.cleaned_data.get(
                        'opzioni_pagamento')
                    if is_valid_form([form.country, form.city, form.route, form.cap]):
                        billing_address = BillingAddress(
                            user=self.request.user,
                            country=form.country,
                            city=form.city,
                            route=form.route,
                            cap=form.cap,
                            house_number=form.house_number,
                            note=form.note
                        )
                        billing_address.save()
                        order_apps = order.apps.all()
                        order_apps.update(is_ordered=True)
                        order.billing_address = billing_address
                        for app in order_apps:
                            app.product.ordered = True
                            app.product.sales_count += 1
                            app.product.data = timezone.now()
                            app.product.save()
                            app.save()

                        order.billing_address = billing_address
                        order.is_ordered = True
                        order.ordered_date = timezone.now()
                        order.save()
                        payment = Payment()
                        payment.user = self.request.user
                        payment.amount = order.get_total()
                        payment.order = order
                        payment.save()

                        form.save_info = form.cleaned_data.get('save_info')
                        if form.save_info:
                            billing_address.default = True
                            billing_address.save()
                    else:
                        messages.warning(
                            self.request, "Compila tutti i campi per continuare")
                        return redirect('checkout')

            messages.info(
                self.request, "Il tuo ordine è stato inviato, al pagamento effettuato la riceverai per email.")
            return redirect('homepage')

            # messages.warning(self.request, "Il pagamento non è andato a buon fine")
            # return redirect('homepage')
            # return render(self.request, 'core/order/order_summary.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "Non hai nessun ordine in corso")
            return redirect('order_summary')


'''Purchases view'''


class PurchasesView(View):
    model = User
    template_name = '/core/user_purchases.html'

    def get(self, *args, **kwargs):
        user_id = self.request.user.id
        user = User.objects.get(id=user_id)
        user_purchases = Payment.objects.filter(user=user).order_by("-pk")
        paginator = Paginator(user_purchases, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'User': user,
            'purchase_list': page_obj,
            'page_obj': page_obj
        }
        return render(self.request, 'core/user_purchases.html', context)


'''App detail view'''


class AppDetailView(DetailView):
    model = App
    template_name = "core/app.html"

    def is_purchased(self):
        user_id = self.request.user.id
        user = User.objects.get(id=user_id)
        user_purchases = Payment.objects.filter(user=user).order_by("-pk")
        for purchases in user_purchases:
            order = Order.objects.get(id=purchases.order.id, is_ordered=True)
            for app in order.apps.all():
                if app.product.slug == self.kwargs['slug']:
                    return True
        return False


'''
View for check the details of a order
'''


class OrderDisplayView(View):
    model = Order
    template_name = 'core/order/order_display.html'

    def get(self, *argss, **kwargs):
        order_id = self.kwargs['pk']
        order = Order.objects.get(id=order_id, is_ordered=True)
        context = {
            'User': self.request.user,
            'purchase_list': order.apps.all()
        }
        return render(self.request, 'core/order/order_display.html', context)

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        order_id = self.kwargs["pk"]
        order = get_object_or_404(Order, id=order_id)

        if user.id is not order.user.id:
            messages.error(request, "Non puoi accedere a questa pagina !")
            return get_home_view(request)

        return super().dispatch(request, *args, **kwargs)


'''
Filter for categories
'''


def get_category_filter(request, cat):
    object_list = App.objects.filter(
        category=cat, ordered=False).order_by("-pk")
    paginator = Paginator(object_list, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'object_list': object_list,
        'object_list': page_obj,
        'page_obj': page_obj
    }
    return render(request, 'core/homepage_category.html', context)


'''
Show the sales
'''


def get_sales_view(request, username):
    if request.user.username != username:
        messages.info(request, "Non puoi accedere a questa pagina !")
        return get_home_view(request)
    user = get_object_or_404(User, username=username)
    user_apps = App.objects.filter(
        developer=user.pk, ordered=True).order_by('-data')
    paginator = Paginator(user_apps, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {"user": user, "user_apps": page_obj, "page_obj": page_obj}
    return render(request, 'core/user_sales.html', context)


'''Function for search'''


def search(request):
    if "kw" in request.GET:
        querystring = request.GET.get("kw")
        if len(querystring) == 0:
            return redirect("/search/")
        apps = App.objects.filter(
            name__icontains=querystring).order_by("-pk")
        users = User.objects.filter(username__icontains=querystring)
        context = {"apps": apps, "users": users}
        return render(request, 'core/search.html', context)
    else:
        return render(request, 'core/search.html')


'''Function for show the address'''


def address_view(request, username):
    if request.user.username != username:
        messages.info(request, "Non puoi accedere a questa pagina !")
        return get_home_view(request)
    user = get_object_or_404(User, username=username)
    user_address = BillingAddress.objects.filter(user=user.pk)
    context = {"user": user, "user_address": user_address}
    return render(request, 'accounts/address_page.html', context)


'''Function for show details'''


def address_detail(request, pk):
    address = BillingAddress.objects.get(pk=pk)
    if request.user.id != address.user.id:
        messages.info(request, "Non puoi accedere a questa pagina !")
        return get_home_view(request)
    return render(request, 'accounts/address.html', context={"object": address})


'''View for delete address'''


class AddressDeleteView(DeleteView):
    model = BillingAddress
    template_name = 'accounts/address_delete.html'

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        address_id = self.kwargs['pk']
        address = get_object_or_404(BillingAddress, id=address_id)

        if user.id is not address.user.id:
            messages.error(request, "Non puoi accedere a questa pagina !")
            return get_home_view(request)

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        address_id = self.kwargs['pk']
        address = get_object_or_404(BillingAddress, id=address_id)
        user = get_object_or_404(User, username=address.user)
        return reverse_lazy('address_page', kwargs={"username": user})


'''View for modify the address and choose the defaults'''


class AddressChangeView(UpdateView):
    model = BillingAddress
    fields = ('city', 'route', 'country', 'cap', 'default')
    template_name = 'accounts/address_change.html'

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        address_id = self.kwargs['pk']
        address = get_object_or_404(BillingAddress, id=address_id)

        if user.id is not address.user.id:
            messages.error(request, "Non puoi accedere a questa pagina !")
            return get_home_view(request)

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        address_id = self.kwargs['pk']
        address = get_object_or_404(BillingAddress, id=address_id)
        user = get_object_or_404(User, username=address.user)
        return reverse_lazy('address_page', kwargs={"username": user})


'''View for show the app by increasing price'''


class IncreasingPriceView(ListView):
    model = App
    paginate_by = 4
    template_name = "core/app_page.html"
    queryset = App.objects.filter(ordered=False).order_by("price")


'''View for show the app by decreasing price'''


class DecreasingPriceView(ListView):
    model = App
    paginate_by = 4
    template_name = "core/app_page.html"
    queryset = App.objects.filter(ordered=False).order_by("-price")


'''View for show only android apps'''


class AndroidDevicesView(ListView):
    model = App
    paginate_by = 4
    template_name = "core/app_page.html"
    queryset = App.objects.filter(
        device=Devices.android.name, ordered=False).order_by("-pk")


'''View for show only iOS apps'''


class IOSDevicesView(ListView):
    model = App
    paginate_by = 4
    template_name = "core/app_page.html"
    queryset = App.objects.filter(
        device=Devices.ios.name, ordered=False).order_by("-pk")


'''Function for get the graphs data'''


def sales_graph(request, username):
    now = datetime.datetime.now()
    start_date = int(now.strftime("%m"))
    if request.user.username != username:
        messages.error(request, "Non puoi accedere a questa pagina !")
        return get_home_view(request)
    user = get_object_or_404(User, username=username)
    user_apps = App.objects.filter(
        developer=user.pk, ordered=True, data__month=start_date)
    apps = {}

    for x in user_apps:
        day = x.data.strftime("%d")
        if day in apps:
            apps[day] += 1
        else:
            apps[day] = 1

    apps_json = json.dumps(apps)
    context = {'apps': apps_json, }
    return render(request, 'core/sales_graph.html', context)
