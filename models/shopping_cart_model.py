#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2017/3/1.

from argeweb import BasicModel
from argeweb import Fields
from plugins.application_user.models.application_user_model import ApplicationUserModel
from plugins.order.models.freight_type_model import FreightTypeModel


class ShoppingCartModel(BasicModel):
    title = Fields.StringProperty(verbose_name=u'購物車名稱', default=u'預設')
    user = Fields.ApplicationUserProperty(verbose_name=u'使用者')
    total_size = Fields.FloatProperty(verbose_name=u'尺寸合計', default=0.0)
    total_volume = Fields.FloatProperty(verbose_name=u'體積合計', default=0.0)
    total_price = Fields.FloatProperty(verbose_name=u'金額合計', default=0.0)
    total_weight = Fields.FloatProperty(verbose_name=u'重量總重', default=0.0)
    total_volumetric_weight = Fields.FloatProperty(verbose_name=u'材積總重', default=0.0)
    cost_for_items = Fields.FloatProperty(verbose_name=u'成本(項目)', default=0.0, tab_page=4)
    freight = Fields.FloatProperty(verbose_name=u'運費', default=0.0)
    freight_type = Fields.KeyProperty(verbose_name=u'運送方式', kind=FreightTypeModel)

    try:
        from plugins.supplier.models.supplier_model import SupplierModel
    except ImportError:
        class SupplierModel(BasicModel):
            pass
    supplier = Fields.CategoryProperty(verbose_name=u'供應商', kind=SupplierModel)

    @classmethod
    def get_or_create(cls, user, supplier=None, supplier_key=None):
        if supplier is not None and supplier_key is None:
            supplier_key = supplier.key
        cart = cls.query(cls.user == user.key, cls.supplier == supplier_key).get()
        if cart is None:
            cart = cls()
            cart.user = user.key
            if supplier_key:
                cart.supplier = supplier_key
            cart.put()
        return cart

    def get_shopping_cart_item(self, product, spec, item_order_type):
        from shopping_cart_item_model import ShoppingCartItemModel
        return ShoppingCartItemModel.get_or_create(self, self.user, product, spec, item_order_type)

    @property
    def items(self):
        from shopping_cart_item_model import ShoppingCartItemModel
        return ShoppingCartItemModel.query(ShoppingCartItemModel.cart==self.key).fetch()

    def clean(self):
        if len(self.items) == 0:
            self.key.delete()

    def calc_size_weight_price_and_put(self, items=None):
        if items is None:
            items = self.items
        total_volume = 0.0
        total_size = 0.0
        total_price = 0.0
        total_weight = 0.0
        total_volumetric_weight = 0.0
        total_cost_for_items = 0.0
        for cart_item in items:
            total_size += cart_item.quantity * (cart_item.size_1 + cart_item.size_2 + cart_item.size_3)
            total_volume += cart_item.quantity * cart_item.size_1 * cart_item.size_2 * cart_item.size_3
            total_price += cart_item.quantity * cart_item.price
            total_weight += cart_item.quantity * cart_item.weight
            total_volumetric_weight += cart_item.quantity * cart_item.volumetric_weight()
            total_cost_for_items += cart_item.quantity * cart_item.cost
        self.total_volume = total_volume
        self.total_size = total_size
        self.total_price = total_price
        self.total_weight = total_weight
        self.total_volumetric_weight = total_volumetric_weight
        self.cost_for_items = total_cost_for_items
        self.put()
