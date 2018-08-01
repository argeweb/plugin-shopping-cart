#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2017/3/1.


from argeweb import Controller, scaffold, route_menu


class ShoppingCart(Controller):
    @route_menu(list_name=u'super_user', group=u'記錄查看', need_hr=True, text=u'購物車', sort=1331)
    def admin_list(self):
        return scaffold.list(self)
