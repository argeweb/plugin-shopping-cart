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


class Form(Controller):
    class Meta:
        components = (scaffold.Scaffolding, Pagination, Search, CSRF)
        default_view = 'json'
        Model = ShoppingCartItemModel

    class Scaffold:
        display_in_form = ['user_name', 'account', 'is_enable', 'sort', 'created', 'modified']

    def check_with_sku(self, allow_get=False):
        self.context['data'] = {'result': 'failure'}
        if allow_get is False and self.request.method != 'POST':
            return self.abort(404)
        if self.application_user is None:
            self.context['message'] = u'請先登入。'
            return True
        self.sku = self.params.get_ndb_record('sku')
        if self.sku is None:
            self.context['message'] = u'該品項不存在或無法購買'
            return True

    @route
    @add_authorizations(auth.check_user)
    @route_with(name='form:shopping_cart:add_item')
    def add_item(self):
        if self.check_with_sku():
            return
        order_type = 0
        if self.params.get_string('order_type') == u'pre_order':
            order_type = 1
        m = self.meta.Model.get_or_create_with_sku(self.application_user, self.sku, self.params.get_integer('quantity'), order_type)
        if m.can_add_to_order is False:
            self.context['message'] = u'失敗，庫存量不足或已停售。'
            return
        self.context['data'] = {'result': 'success'}
        self.context['message'] = u'已成功加入。'

    @route
    @add_authorizations(auth.check_user)
    @route_with(name='form:shopping_cart:remove_item')
    def remove_item(self):
        if self.check_with_sku(True):
            return
        self.context['message'] = u'已刪除'
        self.context['data'] = {'result': 'success'}
        return scaffold.delete(self, self.sku.key)

    @route
    @add_authorizations(auth.check_user)
    @route_with(name='form:shopping_cart:change_quantity')
    def change_quantity(self):
        self.context['data'] = {'result': 'failure'}
        if self.request.method != 'POST':
            return self.abort(404)
        length = self.params.get_integer('length')
        for index in xrange(0, length):
            item = self.params.get_ndb_record('key_%s' % index)
            if item is not None:
                item.change_quantity(self.params.get_integer('quantity_%s' % index))
                item.put()
        self.context['data'] = {'result': 'success'}
        self.context['message'] = u'已更新'

    @route
    @add_authorizations(auth.check_user)
    @route_with(name='form:shopping_cart:check_sku')
    def check_sku(self):
        if self.check_with_sku():
            return
