from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index,name='index'),
    path('register',views.register,name='register'),
    path('login',views.login,name='login'),
    path('logout',views.logout,name='logout'),
    path('products', views.product_list, name='product_list'),
    path('cart',views.cart_view,name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('order',views.order,name='order'),
    path('cart/remove/<str:product_name>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/add/<str:product_name>/', views.adding, name='adding'),
    path('place-order/', views.place_order, name='place_order'),
    path('order-success/', views.order_success, name='order_success'),
    path('order-history/', views.order_history, name='order_history'),

]