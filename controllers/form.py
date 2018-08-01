#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2017/3/1.
from google.appengine.ext import ndb

from argeweb import Controller, scaffold, route_with, route, require_post
from argeweb import auth, add_authorizations
from argeweb.components.pagination import Pagination
from argeweb.components.csrf import CSRF, csrf_protect
from argeweb.components.search import Search
from ..models.shopping_cart_model import ShoppingCartModel
from ..models.shopping_cart_item_model import ShoppingCartItemModel


class Form(Controller):
    class Meta:
        default_view = 'json'
        Model = ShoppingCartItemModel

    class Scaffold:
        display_in_form = ['user_name', 'account', 'is_enable', 'sort', 'created', 'modified']

    def check_with_spec(self, allow_get=False):
        self.context['data'] = {'result': 'failure'}
        if allow_get is False and self.request.method != 'POST':
            return self.abort(404)
        # TODO 無登入狀態的購物車
        if self.application_user is None:
            return self.json_failure_message(u'請先登入')
        self.spec = self.params.get_ndb_record('spec')
        if self.spec is None:
            return self.json_failure_message(u'該品項規格不存在或無法購買')
        self.product = self.spec.product_object.get()
        if self.product is None:
            return self.json_failure_message(u'該品項不存在或無法購買')

    @route
    @route_with(name='form:shopping_cart:add_item')
    def add_item(self):
        self.check_with_spec()
        self.fire(event_name='before_cart_item_change')

        # 支援供應商模組
        supplier = None
        if hasattr(self, 'use_supplier') and self.use_supplier is True:
            # 若訂購模組需要依供應商區分訂單的話
            if hasattr(self, 'create_with_supplier') and self.create_with_supplier is True:
                supplier = self.product.supplier

        # 支援產品庫存模組
        #  0=訂購(無庫存), 1=現貨, 2預購
        order_type = 0
        if hasattr(self, 'use_product_stock') and self.use_product_stock is True:
            ot = self.params.get_string('order_type', u'stock')
            if ot == u'stock':
                order_type = 1
            if ot == u'pre_order':
                order_type = 2

        if self.application_user is None:
            return self.json_failure_message(u'請先登入')
        cart = ShoppingCartModel.get_or_create(self.application_user, supplier_key=supplier)

        item = cart.get_shopping_cart_item(self.product, self.spec, order_type)
        self.fire(
            event_name='shopping_cart_item_change_quantity',
            item=item,
            quantity=self.params.get_integer('quantity')
        )
        item.put()
        cart.calc_size_weight_price_and_put()
        self.fire(event_name='after_cart_item_change', item=item)
        if item.can_add_to_order is False:
            self.context['message'] = u'失敗，庫存量不足或已停售。'
            return
        self.context['data'] = {'result': 'success'}
        self.context['message'] = u'已成功加入。'

    @route
    @route_with(name='form:shopping_cart:remove_item')
    def remove_item(self):
        if self.check_with_spec(True):
            return
        self.fire(event_name='before_cart_item_change')

        # 支援供應商模組
        supplier = None
        if hasattr(self, 'use_supplier') and self.use_supplier is True:
            # 若訂購模組需要依供應商區分訂單的話
            if hasattr(self, 'create_with_supplier') and self.create_with_supplier is True:
                supplier = self.product.supplier
        cart = ShoppingCartModel.get_or_create(self.application_user, supplier_key=supplier)
        scaffold.delete(self, self.spec.key)
        cart.clean()
        self.json_success_message(u'已刪除')

    @route
    @require_post
    @route_with(name='form:shopping_cart:change_quantity')
    def change_quantity(self):
        self.context['data'] = {'result': 'failure'}

        length = self.params.get_integer('length')
        for index in xrange(0, length):
            item = self.params.get_ndb_record('key_%s' % index)
            if item is not None:
                self.fire(
                    event_name='shopping_cart_item_change_quantity',
                    item=item,
                    quantity=self.params.get_integer('quantity_%s' % index)
                )
                item.put()
                cart = item.cart.get()
                cart.calc_size_weight_price_and_put()
        return self.json_success_message(u'已更新')

    @route
    @require_post
    @route_with(name='form:shopping_cart:calc_amount')
    def calc_amount(self):
        freight_type = self.params.get_ndb_record('freight_type')
        if freight_type is None:
            return self.json_failure_message(u'寄送方式不存在')
        carts = ShoppingCartModel.find_by_properties(user=self.application_user.key).fetch()
        freights = freight_type.items.fetch()
        freight_total = 0.0

        data = []
        for cart in carts:
            self.fire(
                event_name='calc_freight_amount',
                target=cart,
                freight_data=freights
            )
            freight_total += cart.freight_amount
            data.append({
                'cart': cart.name,
                'freight': cart.freight_amount
            })
        self.json({
            'result': 'success',
            'message': u'運費已更新',
            'items': [
                {
                    'name': 'freight',
                    'title': '運費',
                    'amount': freight_total,
                    'calc': 'add',
                }
            ],
            'data': data
        })


