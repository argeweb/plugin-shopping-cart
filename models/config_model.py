#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/12.

from argeweb import BasicConfigModel
from argeweb import Fields


class ConfigModel(BasicConfigModel):
    title = Fields.HiddenProperty(verbose_name=u'設定名稱', default=u'購物車設定')

    use_sku = Fields.BooleanProperty(verbose_name=u'使用產品庫存模組', default=False)
    use_supplier = Fields.BooleanProperty(verbose_name=u'使用供應商模組', default=True)


