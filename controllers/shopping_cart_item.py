#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2017/3/1.

from argeweb import Controller, scaffold


class ShoppingCartItem(Controller):
    class Scaffold:
        display_in_list = ['user', 'order_type', 'title', 'spec_full_name', 'price', 'quantity', 'created']

    def admin_list(self):
        def query_factory_only_codefile(controller):
            m = self.meta.Model
            return m.query().order(-m.sort, -m.key)

        self.scaffold.query_factory = query_factory_only_codefile
        return scaffold.list(self)