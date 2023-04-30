import json
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from channels.layers import get_channel_layer
from django.dispatch import receiver
from asgiref.sync import async_to_sync

# Create your models here.

STATE_CHOICES = (
    ("1", "provience no. 1"),
    ("2", "provience no. 2"),
    ("3", "provience no. 3"),
    ("4", "provience no. 4"),
    ("5", "provience no. 5"),
    ("6", "provience no. 6"),
    ("7", "provience no. 7"),
)


class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    locality = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    zipcode = models.IntegerField()
    state = models.CharField(choices=STATE_CHOICES, max_length=50)

    def __str__(self):
        return str(self.id)


CATEGORY_CHOICES = (
    ("M", "Mobile"),
    ("L", "Laptop"),
    ("TW", "Top Wear"),
    ("BW", "Bottom Wear"),
)


class Product(models.Model):
    title = models.CharField(max_length=255)
    selling_price = models.FloatField()
    discounted_price = models.FloatField()
    description = models.TextField()
    brand = models.CharField(max_length=255)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    product_image = models.ImageField(upload_to="productimg")

    def __str__(self):
        return str(self.id)


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.id)

    @property
    def total_cost(self):
        return self.quantity * self.product.discounted_price


STATUS_CHOICES = (
    ("Accepted", "Accepted"),
    ("Packed", "Packed"),
    ("On The Way", "On The Way"),
    ("Delivered", "Delivered"),
    ("Cancel", "Cancel"),
)


class OrderPlaced(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    ordered_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="Pending")

    @property
    def total_cost(self):
        return self.quantity * self.product.discounted_price

    @staticmethod
    def send_status(uid):
        ins = OrderPlaced.objects.filter(user=uid)
        obj = []
        for instance in ins:
            data = {}
            data["status"] = instance.status
            data["oid"] = instance.id
            prog = 0
            if instance.status == "Accepted":
                prog = 25
            elif instance.status == "Packed":
                prog = 50
            elif instance.status == "On The Way":
                prog = 75
            elif instance.status == "Delivered":
                prog = 100
            data["prog"] = prog
            obj.append(data)
        return obj


@receiver(post_save, sender=OrderPlaced)
def order_status_handler(sender, instance, created, **kwargs):
    if not created:
        channel_layer = get_channel_layer()
        data = {}
        data["status"] = instance.status
        data["oid"] = instance.id
        prog = 0
        if instance.status == "Accepted":
            prog = 25
        elif instance.status == "Packed":
            prog = 50
        elif instance.status == "On The Way":
            prog = 75
        elif instance.status == "Delivered":
            prog = 100
        data["prog"] = prog
        async_to_sync(channel_layer.group_send)(
            "order_%s" % instance.user.id,
            {"type": "order_status", "value": json.dumps(data)},
        )
