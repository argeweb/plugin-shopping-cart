#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/12.

from argeweb import ViewFunction
from models.shopping_cart_item_model import get_quantity_with_shopping_car
from models import *

ViewFunction.register(get_quantity_with_shopping_car)

plugins_helper = {
    'title': u'購物車模組',
    'desc': u'將產品及其 SKU 加入至會員帳戶中，並與 SKU 庫存量連動',
    'controllers': {
        'shopping_cart_item': {
            'group': u'購物車',
            'actions': [
                {'action': 'list', 'name': u'購物車'},
                {'action': 'add', 'name': u'新增購物車'},
                {'action': 'edit', 'name': u'編輯購物車'},
                {'action': 'view', 'name': u'檢視購物車'},
                {'action': 'delete', 'name': u'刪除購物車'},
                {'action': 'plugins_check', 'name': u'啟用停用模組'},
            ]
        }
    }
}
