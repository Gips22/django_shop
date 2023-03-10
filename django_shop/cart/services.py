"""Бизнес-логика для вьюх приложения cart вынесена сюда"""
from decimal import Decimal
from typing import Dict, List, Union

from django.conf import settings
from django.shortcuts import get_object_or_404

from cart.forms import CartAddProductForm
from shop.models import Product


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def get_cart_total_price(self, cart_items: List[Dict[str, Union[str, int, Decimal]]]) -> Decimal:
        """
        Вычисляет общую стоимость всех товаров в корзине.
        """
        return sum(Decimal(item['total_price']) for item in cart_items)

    def get_cart_items_with_products(self):
        """
        Возвращает список словарей, содержащий товары в корзине и их соответствующие объекты Product.
        """
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart_items = []

        for product in products:
            cart_item = self.cart[str(product.id)]
            cart_item['product'] = product
            cart_item['total_price'] = Decimal(cart_item['price']) * cart_item['quantity']
            cart_item['update_quantity_form'] = CartAddProductForm(initial={'quantity': cart_item['quantity']})
            cart_items.append(cart_item)

        return cart_items

    def add_to_cart(self, product_id: int, quantity: int, overwrite_qty: bool = False) -> None:
        """
        Добавляет товар в корзину или обновляет его количество, если товар уже в корзине.
        """
        product = get_object_or_404(Product, id=product_id)
        product_id = str(product_id)

        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}

        if overwrite_qty:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity

        self.session.modified = True

    def remove_from_cart(self, product_id: int) -> None:
        """
        Удаляет товар из корзины.
        """
        product_id = str(product_id)

        if product_id in self.cart:
            del self.cart[product_id]
            self.session.modified = True

    def clear_cart(self) -> None:
        """
        Очищает корзину.
        """
        self.session[settings.CART_SESSION_ID] = {}
        self.session.modified = True

    def get_cart(self) -> Dict[str, Dict[str, Union[str, int]]]:
        """
        Возвращает корзину из сессии или пустой словарь, если ее нет.
        """
        return self.session.get(settings.CART_SESSION_ID, {})


# def get_cart_total_price(cart_items: List[Dict[str, Union[str, int, Decimal]]]) -> Decimal:
#     """
#     Вычисляет общую стоимость всех товаров в корзине.
#     """
#     return sum(item['total_price'] for item in cart_items)
#
#
# def get_cart_items_with_products(cart):
#     """
#     Возвращает список словарей, содержащий товары в корзине и их соответствующие объекты Product.
#     """
#     product_ids = cart.keys()
#     products = Product.objects.filter(id__in=product_ids)
#     cart_items = []
#
#     for product in products:
#         cart_item = cart[str(product.id)]
#         cart_item['product'] = product
#         cart_item['total_price'] = Decimal(cart_item['price']) * cart_item['quantity']
#         cart_item['update_quantity_form'] = CartAddProductForm(initial={'quantity': cart_item['quantity']})
#         cart_items.append(cart_item)
#
#     return cart_items
#
#
# def add_to_cart(request, product_id: int, quantity: int, overwrite_qty: bool = False) -> None:
#     """
#     Добавляет товар в корзину или обновляет его количество, если товар уже в корзине.
#     """
#     cart = get_cart(request)
#     product = get_object_or_404(Product, id=product_id)
#     product_id = str(product_id)
#
#     if product_id not in cart:
#         cart[product_id] = {'quantity': 0, 'price': str(product.price)}
#
#     if overwrite_qty:
#         cart[product_id]['quantity'] = quantity
#     else:
#         cart[product_id]['quantity'] += quantity
#
#     request.session[settings.CART_ID] = cart
#     request.session.modified = True
#
#
# def remove_from_cart(request, product_id: int) -> None:
#     """
#     Удаляет товар из корзины.
#     """
#     cart = get_cart(request)
#     product_id = str(product_id)
#
#     if product_id in cart:
#         del cart[product_id]
#         request.session[settings.CART_ID] = cart
#         request.session.modified = True
#
#
# def clear_cart(request) -> None:
#     """
#     Очищает корзину.
#     """
#     request.session[settings.CART_ID] = {}
#     request.session.modified = True
#
#
# def get_cart(request) -> Dict[str, Dict[str, Union[str, int]]]:
#     """
#     Возвращает корзину из сессии или пустой словарь, если ее нет.
#     """
#     return request.session.get(settings.CART_ID, {})
