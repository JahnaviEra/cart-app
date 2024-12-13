from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.db.models import Sum
from django.contrib.auth.models import User,auth
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Cart,Cart_Items,Orders
import json
from datetime import timedelta

def index(request):
    products = Cart.objects.all()

    if request.user.is_authenticated:
        cart_items = Cart_Items.objects.filter(user=request.user).first()
        if cart_items and cart_items.product_names:
            # Decode product_names JSON string and sum up the values
            product_dict = json.loads(cart_items.product_names)
            cart_count = sum(product_dict.values())
        else:
            cart_count = 0
    else:
        cart_count = 0  # Default to 0 if the user is not authenticated

    return render(request, 'index.html', {'products': products, 'cart_count': cart_count})

def register(request):
    if request.method=='POST':
        username=request.POST['username']
        email=request.POST['email']
        password1=request.POST['password1']
        password2=request.POST['password2']


        if not username or not email or not password1 or not password2:
            messages.error(request, "All fields are required. Please fill them in.")
            return redirect('register')
        
        if password1==password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, "Username already exists. Please try a different one.")
                return redirect('register')
            elif User.objects.filter(email=email).exists():
                messages.info(request, "An account with this email already exists.")
                return redirect('register')
            else:
                user=User.objects.create_user(username=username,password=password1,email=email)
                user.save();
                messages.success(request, "Account created successfully! You can now log in.")
                return redirect('login')
        else:
            messages.error(request, "Passwords do not match. Please try again.")
            return redirect('register')
    else:
        return render(request,'register.html')
    
def login(request):
    if request.method=="POST":
        username=request.POST['username']
        password=request.POST['password1']
        user=auth.authenticate(username=username,password=password)
        if user is not None:
            auth.login(request,user)
            return redirect("/")
        else:
            messages.info(request,"user data is invalid, please register account..")
            return redirect("login")
    else:
        return render(request,'login.html')
    

def logout(request):
    auth.logout(request)
    return redirect('/')

def product_list(request):
    products = Cart.objects.all()  # Get all Buy objects from the database
    return render(request, 'index.html', {'products': products})

@login_required
def cart_view(request):
    if request.user.is_authenticated:
        # Get the cart items for the logged-in user
        cart_items = Cart_Items.objects.filter(user=request.user)
        
        products_in_cart = []  # This will hold the products with names, quantities, and total price
        total_price = 0  # Initialize total price
        
        # Loop through the cart items and add them to the products_in_cart list
        for item in cart_items:
            if item.product_names:
                product_dict = json.loads(item.product_names)  # Load the product dictionary
                for product_name, quantity in product_dict.items():
                    # Retrieve the product's price, assuming the price is available in the Cart model or Product model
                    # If the price is stored in a separate model, you need to fetch it. Here's an example:
                    product = get_object_or_404(Cart, product_name=product_name)  # Assuming Product model has a 'name' field
                    
                    # Calculate the total price for this product based on its price and quantity
                    product_total_price = product.price * quantity
                    
                    # Add product details to the list
                    products_in_cart.append({
                        'product_name': product_name,
                        'quantity': quantity,
                        'total_price': product_total_price,
                    })
                    
                    # Accumulate the total price of all items in the cart
                    total_price += product_total_price


        if not products_in_cart:
            messages.info(request,"Your cart is empty. Please add products to place order.")
            return render(request, 'cart.html', {'cart_items': products_in_cart, 'total_price': total_price, 'message': messages})
        
        
        # Render the cart page with the cart items and total price
        return render(request, 'cart.html', {'cart_items': products_in_cart, 'total_price': total_price})
    
    else:
        return redirect('login')

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Cart, id=product_id)
    user = request.user

    # Check if a Purchase record already exists for the user
    cart_item, created = Cart_Items.objects.get_or_create(user=user)

    # Add the product to the cart
    cart_item.add_product(product_name=product.product_name, product_price=product.price, quantity=1)
    cart_item.save()

    return redirect('/')  #

def order(request):
    return render(request,'order.html')

@login_required
def remove_from_cart(request, product_name):
    cart_item = get_object_or_404(Cart_Items, user=request.user)
    product = get_object_or_404(Cart, product_name=product_name)
    cart_item.remove_product(product_name=product_name, product_price=product.price)
    return redirect('cart')

@login_required
def adding(request, product_name):
    cart_item = get_object_or_404(Cart_Items, user=request.user)
    product = get_object_or_404(Cart, product_name=product_name)
    cart_item.add(product_name=product_name, product_price=product.price)
    return redirect('cart')

@login_required
def place_order(request):
    if request.method == 'POST':
        user = request.user

        # Get the cart items for the user
        try:
            cart_items = Cart_Items.objects.get(user=user)
            product_dict = json.loads(cart_items.product_names)  # Convert JSON to Python dictionary

            # Calculate total price and products list if not already available
            total_price = 0.0
            product_details = {}
            for product_name, quantity in product_dict.items():
                # Get product details from your Product model
                product = get_object_or_404(Cart, product_name=product_name)
                product_details[product_name] = {
                    'quantity': quantity,
                    'price': product.price,
                    'total_price': product.price * quantity,
                }
                total_price += product.price * quantity

            # Save the order in the Orders model
            order = Orders.objects.create(
                user=user,
                address=request.POST['address'],
                payment_method=request.POST['paymentMethod'],
                mobile=request.POST['mobile'],
                products=json.dumps(product_details),  # Save product details as JSON
                total_price=total_price
            )

            # Clear the cart after the order is placed
            cart_items.product_names = json.dumps({})
            cart_items.quantity = 0
            cart_items.total_price = 0.00
            cart_items.save()

            # Redirect to the order success page
            return redirect('order_success')

        except Cart_Items.DoesNotExist:
            # Handle the case where the cart is empty
            return redirect('cart')  # Redirect back to the cart if no items exist

    return redirect('cart')  # If the request method is not POST, redirect to the cart page

# @login_required
# def place_order(request):
#     if request.method == 'POST':
#         # Assuming the user is logged in
#         user = request.user

#         # Reset the cart (clear cart)
#         try:
#             cart = Cart_Items.objects.get(user=user)
#             cart.product_names = json.dumps({})  # Clear product names
#             cart.quantity = 0  # Reset quantity to 0
#             cart.total_price = 0.00  # Reset total price
#             cart.save()  # Save the updated cart
#         except Cart_Items.DoesNotExist:
#             return JsonResponse({'error': 'Cart not found'}, status=400)

#         # Here you can add the logic to process the order (e.g., store it in an Orders table)

#         # After clearing the cart, redirect to a success page or display a success message
#         return redirect('order_success')  # Redirect to a success page

#     return redirect('cart')  # If the request method is not POST, redirect to the cart page

def order_success(request):
    return render(request, 'order_success.html')



@login_required
def order_history(request):
    # Fetch orders for the logged-in user, ordered by date
    orders = Orders.objects.filter(user=request.user).order_by('-order_date')

    # Prepare data for rendering
    order_details = []
    for order in orders:
        # Load product details from JSON
        product_dict = json.loads(order.products)
        product_list = []
        
        for product_name, details in product_dict.items():
            # Here, details is expected to be a dictionary with 'quantity', 'price', 'total_price'
            product_list.append({
                'product_name': product_name,
                'quantity': details['quantity'],
                'price': details['price'],
                'total_price': details['total_price'],
            })
        order.order_date = order.order_date + timedelta(hours=5, minutes=30)
        # Append order details
        order_details.append({
            'id': order.id,
            'order_date': order.order_date,
            'total_price': order.total_price,
            'products': product_list,
        })

    return render(request, 'order_history.html', {'order_details': order_details})
