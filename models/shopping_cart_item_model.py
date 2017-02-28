#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/12.

from argeweb import BasicModel
from argeweb import Fields
from plugins.product_stock.models.stock_keeping_unit_model import StockKeepingUnitModel
from plugins.application_user.models.application_user_model import ApplicationUserModel
from plugins.product.models.product_config_model import ProductConfigModel
from shopping_cart_model import ShoppingCartModel
from time import time


class ShoppingCartItemModel(BasicModel):
    class Meta:
        label_name = {
            'title_lang_zhtw': u'標題',
            'content_lang_zhtw': u'內容',
        }
    name = Fields.StringProperty(verbose_name=u'系統編號')
    sku = Fields.KeyProperty(verbose_name=u'最小庫存單位', kind=StockKeepingUnitModel)
    user = Fields.KeyProperty(verbose_name=u'使用者', kind=ApplicationUserModel)

    title = Fields.StringProperty(verbose_name=u'產品名稱')
    product_no = Fields.StringProperty(verbose_name=u'產品編號')
    product_name = Fields.StringProperty(verbose_name=u'產品圖片', default=u'')
    product_image = Fields.StringProperty(verbose_name=u'產品圖片', default=u'')
    sku_full_name = Fields.StringProperty(verbose_name=u'產品最小庫存名稱')
    spec_full_name = Fields.StringProperty(verbose_name=u'完整規格名稱')
    price = Fields.FloatProperty(verbose_name=u'銷售價格', default=-1)
    quantity = Fields.IntegerProperty(verbose_name=u'數量', default=0)
    quantity_has_count = Fields.IntegerProperty(verbose_name=u'已計入庫存的數量', default=0)
    can_add_to_order = Fields.BooleanProperty(verbose_name=u'加至訂單中', default=False)
    expired_time = Fields.FloatProperty(verbose_name=u'庫存回收時間')

    #  0 = 現貨, 1=預購
    order_type = Fields.StringProperty(verbose_name=u'訂購方式')
    order_type_value = Fields.IntegerProperty(verbose_name=u'訂購方式(值)')

    @classmethod
    def get(cls, user, sku, order_type_value=0):
        return cls.query(cls.sku==sku.key, cls.user==user.key, cls.order_type_value==order_type_value).get()

    @classmethod
    def get_or_create(cls, user, sku, quantity=0, order_type_value=0):
        product = sku.product.get()
        item = cls.query(cls.sku==sku.key, cls.user==user.key, cls.order_type_value==order_type_value).get()
        if item is None:
            item = cls()
            item._sku = sku
            item.sku = sku.key
            item.user = user.key
        item.title = product.title
        item.product_no = product.product_no
        item.product_image = product.image
        item.product_name = product.name
        item.sku_full_name = sku.sku_full_name
        item.spec_full_name = sku.spec_full_name
        if sku.use_price:
            item.price = sku.price
        else:
            item.price = product.price
            item.order_type_value = order_type_value
        if order_type_value == 0:
            item.order_type = u'現貨'
            namespace = product._key._Key__namespace
            config = ProductConfigModel.find_by_name(namespace)
            if config.stock_recover:
                item.expired_time = time() + config.stock_recover_time
            else:
                item.expired_time = time() + 525600
            can_use_quantity = sku.quantity - sku.estimate + int(item.quantity_has_count)
            old_quantity_has_count = item.quantity_has_count
            if can_use_quantity >= quantity and product.can_order:
                item.can_add_to_order = True
                item.quantity = quantity
                item.quantity_has_count = quantity
            else:
                item.can_add_to_order = False
                item.quantity = 0
                item.quantity_has_count = 0
            sku.estimate = sku.estimate - abs(old_quantity_has_count) + abs(item.quantity)
            sku.put()
        else:
            if product.can_pre_order:
                item.can_add_to_order = True
                item.quantity = quantity
                item.order_type = u'預購'
            else:
                item.can_add_to_order = False
                item.quantity = 0
                item.order_type = u'預購'
            sku.pre_order_quantity = sku.pre_order_quantity - abs(int(item.quantity_has_count)) + abs(item.quantity)
            sku.put()
        item.put()
        return item

    @classmethod
    def all_with_user(cls, user):
        key = None
        if user is not None:
            key = user.key
        return cls.query(cls.user==key).order(-cls.sort)

    @classmethod
    def before_delete(cls, key):
        item = key.get()
        if item.order_type_value == 0:
            if item.quantity > 0:
                sku = item.sku.get()
                sku.estimate = sku.estimate - item.quantity_has_count
                sku.put()

    def quantity_can_be_order(self, user=None, sku=None):
        if sku is None:
            sku = self.sku.get()
        if self.order_type_value > 0:
            return 999
        if user:
            return sku.quantity - sku.estimate + self.quantity
        return sku.quantity - sku.estimate


def get_quantity_with_shopping_car(sku, user=None, *args, **kwargs):
    if user:
        cart_item = ShoppingCartItemModel.get(user, sku)
        if cart_item:
            return cart_item.quantity_can_be_order(user, sku)
    return sku.quantity - sku.estimate
