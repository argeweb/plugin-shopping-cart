#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/12.

from argeweb import Controller, scaffold, route_menu, route_with, route
from argeweb.components.pagination import Pagination
from argeweb.components.search import Search


class ShoppingCartItem(Controller):
    class Meta:
        components = (scaffold.Scaffolding, Pagination, Search)
        pagination_actions = ('list',)
        pagination_limit = 50

    class Scaffold:
        display_in_list = ('user', 'order_type', 'title', 'spec_full_name', 'price', 'quantity', 'created')

    @route_menu(list_name=u'backend', text=u'購物車內容', sort=310, group=u'內容管理', need_hr=True)
    def admin_list(self):
        def query_factory_only_codefile(controller):
            m = self.meta.Model
            return m.query().order(-m.sort, -m.key)

        self.scaffold.query_factory = query_factory_only_codefile
        return scaffold.list(self)