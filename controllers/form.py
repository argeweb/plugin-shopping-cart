#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/12.
from datetime import datetime
from argeweb import Controller, scaffold, route_menu, route_with, route, settings
from argeweb import auth, add_authorizations
from argeweb.components.pagination import Pagination
from argeweb.components.csrf import CSRF, csrf_protect
from argeweb.components.search import Search
from plugins.mail import Mail
from ..models.shopping_cart_item_model import ShoppingCartItemModel


class Form(Controller):
    class Meta:
        components = (scaffold.Scaffolding, Pagination, Search, CSRF)
        pagination_actions = ('list',)
        pagination_limit = 50
        default_view = 'json'
        Model = ShoppingCartItemModel

    class Scaffold:
        display_in_form = ('user_name', 'account', 'is_enable', 'sort', 'created', 'modified')

    def check(self):
        self.context['data'] = {'result': 'failure'}
        if self.request.method != 'POST':
            return self.abort(404)
        if self.application_user is None:
            self.context['message'] = u'請先登入。'
            return True

    @route
    @add_authorizations(auth.check_user)
    @route_with(name='form:shopping_cart:add_item')
    def add_item(self):
        if self.check():
            return
        sku = self.params.get_ndb_record('sku')
        if sku is None or sku.can_be_purchased == False:
            self.context['message'] = u'該品項不存在或無法購買'
            return
        order_type = 0
        if self.params.get_string('order_type') == u'pre_order':
            order_type = 1
        m = self.meta.Model.get_or_create(self.application_user, sku, self.params.get_integer('quantity'), order_type)
        if m.quantity < 0:
            self.context['message'] = u'失敗，庫存量不足。'
            return
        self.context['data'] = {'result': 'success'}
        self.context['message'] = u'已成功加入。'

    @route
    @add_authorizations(auth.check_user)
    @route_with(name='form:shopping_cart:remove_item')
    def remove_item(self):
        self.check()

    @route
    @add_authorizations(auth.check_user)
    @route_with(name='form:shopping_cart:change_quantity')
    def change_quantity(self):
        self.check()

    @route
    @add_authorizations(auth.check_user)
    @route_with(name='form:shopping_cart:check_sku')
    def check_sku(self):
        self.check()
