#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2017/3/1.
from argeweb import Controller, scaffold, route_with, route
from argeweb import auth, add_authorizations
from argeweb.components.pagination import Pagination
from argeweb.components.csrf import CSRF, csrf_protect
from argeweb.components.search import Search
from ..models.shopping_cart_item_model import ShoppingCartItemModel


class Data(Controller):
    class Meta:
        components = (scaffold.Scaffolding, Pagination, Search, CSRF)
        default_view = 'json'
        Model = ShoppingCartItemModel

    @route
    @add_authorizations(auth.check_user)
    @route_with('/data/shopping_cart/items', name='data:shopping_cart:items')
    def items(self):
        cu = None
        try:
            from plugins.currency.models.currency_model import CurrencyModel
            cu = CurrencyModel.get_current_or_main_currency_with_controller(self)
        except:
            pass
        data = []
        for item in self.meta.Model.all_with_user(self.application_user).fetch(1000):
            price = item.price
            if cu:
                price = cu.calc(item.price)
            data.append({
                'key': self.util.encode_key(item),
                'order_type': item.order_type,
                'order_type_value': item.order_type_value,
                'product_name': item.product_name,
                'product_image': item.product_image,
                'product_title': item.title,
                'spec_full_name': item.spec_full_name,
                'price': price,
                'quantity_max': item.quantity_can_be_order(self.application_user),
                'quantity': item.quantity,
            })
        self.context["data"] = data
