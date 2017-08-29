#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2017/3/1.

from argeweb import BasicModel
from argeweb import Fields


class ShoppingCartModel(BasicModel):
    name = Fields.StringProperty(required=True, verbose_name=u'識別名稱')
    title = Fields.StringProperty(verbose_name=u'分類名稱', default=u'未命名')
    title_lang_zhtw = Fields.StringProperty(verbose_name=u'繁體中文分類名稱', default=u'未命名')
    title_lang_zhcn = Fields.StringProperty(verbose_name=u'簡體中文分類名稱', default=u'未命名')
    title_lang_enus = Fields.StringProperty(verbose_name=u'英文分類名稱', default=u'未命名')
    is_enable = Fields.BooleanProperty(verbose_name=u'啟用', default=True)
