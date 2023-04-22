from django.shortcuts import render, redirect
from .models import *
from django.views import View
from .froms import CustomerRegistrationForm, CustomerProfileForm
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse


class ProductView(View):
    def get(self, request):
        topwears = Product.objects.filter(category="TW")
        bottomwears = Product.objects.filter(category="BW")
        laptops = Product.objects.filter(category="L")
        return render(
            request,
            "app/home.html",
            {
                "topwears": topwears,
                "bottomwears": bottomwears,
                "laptops": laptops,
            },
        )


class productDetailView(View):
    def get(self, request, pk):
        products = Product.objects.get(id=pk)
        return render(request, "app/productdetail.html", context={"products": products})


def add_to_cart(request):
    usr = request.user
    product_id = request.GET.get("prod_id")
    product = Product.objects.get(id=product_id)
    Cart(user=usr, product=product).save()
    return redirect("/cart")


def show_cart(request):
    if request.user.is_authenticated:
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0.0
        shipping_amount = 70.0
        # list comprehension
        cart_product = [p for p in Cart.objects.all() if p.user == user]
        if cart_product:
            for p in cart_product:
                tempamt = (p.quantity) * p.product.discounted_price
                amount += tempamt

            return render(
                request,
                "app/addtocart.html",
                {
                    "carts": cart,
                    "amount": amount,
                    "total_amount": amount + shipping_amount,
                },
            )
        else:
            return render(request, "app/emptycart.html")
    else:
        return redirect("login")


def plus_cart(request):
    if request.method == "GET":
        prod_id = request.GET["prod_id"]
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity += 1
        c.save()
        amount = 0.0
        shipping_amount = 70.0
        # list comprehension
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamt = (p.quantity) * p.product.discounted_price
            amount += tempamt
        data = {
            "quantity": c.quantity,
            "amount": amount,
            "total_amount": amount + shipping_amount,
        }
        return JsonResponse(data)


def minus_cart(request):
    if request.method == "GET":
        prod_id = request.GET["prod_id"]
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity -= 1
        c.save()
        amount = 0.0
        shipping_amount = 70.0
        # list comprehension
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamt = (p.quantity) * p.product.discounted_price
            amount += tempamt

        data = {
            "quantity": c.quantity,
            "amount": amount,
            "total_amount": amount + shipping_amount,
        }
        return JsonResponse(data)


def remove_cart(request):
    if request.method == "GET":
        prod_id = request.GET["prod_id"]
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.delete()
        amount = 0.0
        shipping_amount = 70.0
        # list comprehension
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamt = p.quantity * p.product.discounted_price
            amount += tempamt

        data = {
            "amount": amount,
            "total_amount": amount + shipping_amount,
        }
        return JsonResponse(data)


def buy_now(request):
    return render(request, "app/buynow.html")


def address(request):
    add = Customer.objects.filter(user=request.user)

    return render(request, "app/address.html", {"add": add, "active": "btn-primary"})


def orders(request):
    op = OrderPlaced.objects.filter(user=request.user)
    return render(request, "app/orders.html", {"op": op})


def login(request):
    return render(request, "app/login.html")


class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, "app/customerregistration.html", {"form": form})

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request, "Success!")
            form.save()
        return render(request, "app/customerregistration.html", {"form": form})


def checkout(request):
    user = request.user
    add = Customer.objects.filter(user=user)
    cart_items = Cart.objects.filter(user=user)
    amount = 0.0
    shipping_amount = 70.0
    # list comprehension
    cart_product = [p for p in Cart.objects.all() if p.user == request.user]
    if cart_product:
        for p in cart_product:
            tempamt = (p.quantity) * p.product.discounted_price
            amount += tempamt
        total_amount = amount + shipping_amount
    return render(
        request,
        "app/checkout.html",
        {"add": add, "totalamount": total_amount, "cart_items": cart_items},
    )


def payment_done(request):
    user = request.user
    custid = request.GET.get("custid")
    customer = Customer.objects.get(id=custid)
    cart = Cart.objects.filter(user=user)
    for c in cart:
        OrderPlaced(
            user=user, customer=customer, product=c.product, quantity=c.quantity
        ).save()
        c.delete()
    return redirect("orders")


# def profile(request):
#     return render(request, "app/profile.html")


class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm()
        return render(
            request, "app/profile.html", {"form": form, "active": "btn-primary"}
        )

    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            usr = request.user
            name = form.cleaned_data["name"]
            locality = form.cleaned_data["locality"]
            city = form.cleaned_data["city"]
            state = form.cleaned_data["state"]
            zipcode = form.cleaned_data["zipcode"]
            reg = Customer(
                user=usr,
                name=name,
                locality=locality,
                city=city,
                state=state,
                zipcode=zipcode,
            )
            reg.save()
            messages.success(request, "Congratulations profile updated successfully")
        return render(
            request, "app/profile.html", {"form": form, "active": "btn-primary"}
        )
