from django.db import models
from django.contrib.auth.models import User,auth
import json
# Create your models here.

class Cart(models.Model):
    product_name=models.CharField(max_length=200)
    img=models.ImageField(upload_to='images')
    desc=models.TextField()
    price=models.IntegerField()


class Cart_Items(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Associate with the User model
    username = models.CharField(max_length=150, editable=False, default='')  # Explicitly store the username
    product_names = models.TextField(default='{}')  # Store a dictionary of products and their quantities as a JSON string
    quantity = models.PositiveIntegerField(default=0)  # Total quantity of all products in the cart
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Total price
    
    def __str__(self):
        return f"Cart for {self.user.username}"

    def add_product(self, product_name, product_price, quantity=1):
        # Check if product_names is empty or not a valid dictionary
        if not self.product_names:
            self.product_names = {}

        # Convert product_names to a dictionary (if it's a string, decode it)
        product_dict = json.loads(self.product_names) if isinstance(self.product_names, str) else self.product_names

        # Add or update the product quantity
        if product_name in product_dict:
            product_dict[product_name] += quantity  # Update quantity if the product is already in the cart
        else:
            product_dict[product_name] = quantity  # Add new product to the cart

        # Update the product_names field with the new dictionary
        self.product_names = json.dumps(product_dict)

        # Update total price and quantity
        self.quantity += quantity
        self.total_price += product_price * quantity

    def add(self, product_name, product_price):
        if not self.product_names:
            return

        product_dict = json.loads(self.product_names)
        if product_name in product_dict:
            product_dict[product_name]+=1
            self.quantity+=1
            self.total_price += product_price
            self.product_names = json.dumps(product_dict)
            self.save()
            


    def remove_product(self, product_name, product_price):
        if not self.product_names:
            return

        product_dict = json.loads(self.product_names)
        if product_name in product_dict:
            product_dict[product_name]-=1
            if product_dict[product_name]==0:
                del product_dict[product_name]
            self.total_price -= product_price
            self.product_names = json.dumps(product_dict)
            self.quantity-=1
            


            # quantity_to_remove = product_dict[product_name]
            # self.quantity -= quantity_to_remove
            # self.total_price -= product_price * quantity_to_remove
            # del product_dict[product_name]
            # self.product_names = json.dumps(product_dict)
            self.save()


    def save(self, *args, **kwargs):
        # Ensure that the username is set from the associated user
        if self.user:
            self.username = self.user.username
        super().save(*args, **kwargs)

    def get_product_names(self):
        # Convert JSON string back to a Python dictionary
        return json.loads(self.product_names)

    def get_total_quantity(self):
        # Calculate the total quantity by summing the quantities of all products in the dictionary
        product_dict = json.loads(self.product_names)
        return sum(product_dict.values())


class Orders(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=150, blank=True, null=True)  # Store username if you want
    address = models.TextField()
    payment_method = models.CharField(max_length=50)
    mobile = models.CharField(max_length=10)
    products = models.TextField(default='{}')  # Store products as a JSON string
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} for {self.user.username}"

    def get_products(self):
        return json.loads(self.products)

    def get_username(self):
        return self.user.username  # Fetch the associated username

    def save(self, *args, **kwargs):
        # Automatically set the username if not provided
        if not self.username:
            self.username = self.user.username
        super().save(*args, **kwargs)
