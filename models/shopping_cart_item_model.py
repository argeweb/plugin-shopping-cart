#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2017/3/1.

from argeweb import BasicModel
from argeweb import Fields
from plugins.application_user.models.application_user_model import ApplicationUserModel
from plugins.product.models.config_model import ConfigModel
from plugins.product.models.product_model import ProductModel
from plugins.product.models.product_specification_model import ProductSpecificationModel
from shopping_cart_model import ShoppingCartModel
from time import time


class ShoppingCartItemModel(BasicModel):
    cart = Fields.KeyProperty(verbose_name=u'購物車', kind=ShoppingCartModel)
    spec = Fields.KeyProperty(verbose_name=u'產品規格', kind=ProductSpecificationModel)
    user = Fields.ApplicationUserProperty(verbose_name=u'使用者')
    product_object = Fields.KeyProperty(verbose_name=u'所屬產品', kind=ProductModel)
    title = Fields.StringProperty(verbose_name=u'產品名稱', default=u'')
    product_name = Fields.StringProperty(verbose_name=u'產品名稱(系統)', default=u'')
    product_no = Fields.StringProperty(verbose_name=u'產品型號', default=u'')
    product_image = Fields.StringProperty(verbose_name=u'產品圖片', default=u'')
    price = Fields.FloatProperty(verbose_name=u'銷售價格', default=-1)
    cost = Fields.FloatProperty(verbose_name=u'成本', default=0.0)
    spec_full_name = Fields.StringProperty(verbose_name=u'完整規格名稱', default=u'')

    # 庫存相關
    try:
        from plugins.product_stock.models.stock_keeping_unit_model import StockKeepingUnitModel
    except ImportError:
        class StockKeepingUnitModel(BasicModel):
            pass
    sku = Fields.KeyProperty(verbose_name=u'最小庫存單位', kind=StockKeepingUnitModel)
    sku_full_name = Fields.StringProperty(verbose_name=u'產品最小庫存名稱')
    expired_time = Fields.FloatProperty(verbose_name=u'庫存回收時間')
    quantity = Fields.IntegerProperty(verbose_name=u'數量', default=0)
    quantity_has_count = Fields.IntegerProperty(verbose_name=u'已計入庫存的數量', default=0)
    can_add_to_order = Fields.BooleanProperty(verbose_name=u'加至訂單中', default=False)

    try:
        from plugins.supplier.models.supplier_model import SupplierModel
    except ImportError:
        class SupplierModel(BasicModel):
            pass
    supplier = Fields.CategoryProperty(kind=SupplierModel, verbose_name=u'供應商')

    #  0=訂購(無庫存), 1=現貨, 2預購
    order_type = Fields.StringProperty(verbose_name=u'訂購方式')
    order_type_value = Fields.IntegerProperty(verbose_name=u'訂購方式(值)')

    size_1 = Fields.FloatProperty(verbose_name=u'長度(公分)', default=10.0)
    size_2 = Fields.FloatProperty(verbose_name=u'寬度(公分)', default=10.0)
    size_3 = Fields.FloatProperty(verbose_name=u'高度(公分)', default=10.0)
    weight = Fields.FloatProperty(verbose_name=u'重量(公斤)', default=10.0)

    @classmethod
    def get_or_create(cls, cart, user, product, spec, order_type=0):
        try:
            user_key = user.key
        except AttributeError:
            user_key = user
        item = cls.query(
            cls.cart==cart.key,
            cls.user==user_key,
            cls.product_object==product.key,
            cls.spec==spec.key,
            cls.order_type_value==order_type
        ).get()
        need_put = False
        if item is None:
            item = cls()
            item.cart = cart.key
            item.user = user_key
            item.product_object = product.key
            item.spec = spec.key
            item.order_type_value = order_type
            item.order_type = [u'訂購', u'現貨', u'預購'][order_type]
            item.spec_full_name = spec.full_name
            item.product_name = product.name
            item.product_image = product.image
            need_put = True
            if order_type == 0:
                item.can_add_to_order = True
        for field_name in ['title', 'product_no', 'price', 'cost', 'size_1', 'size_2', 'size_3', 'weight']:
            if getattr(item, field_name) != getattr(product, field_name):
                setattr(item, field_name, getattr(product, field_name))
                need_put = True
        if need_put:
            item.put()
        return item

    @classmethod
    def get(cls, user, sku, order_type_value=0):
        return cls.query(cls.sku==sku.key, cls.user==user.key, cls.order_type_value==order_type_value).get()

    @classmethod
    def get_or_create_with_spec(cls, user, spec, quantity=0, order_type_value=0):
        product = spec.product_object.get()
        item = cls.query(cls.sku == spec.key, cls.user == user.key, cls.order_type_value == order_type_value).get()
        if item is None:
            item = cls()
            item.spec = spec.key
            item.user = user.key
            item.order_type_value = order_type_value
            item.product_object = product.key
            try:
                item.supplier = product.supplier.get().key
            except:
                pass
            if order_type_value == 0:
                item.order_type = u'訂購'
            else:
                item.order_type = u'預購'
        item._spec = spec
        item._product = product
        item.title = product.title
        item.product_no = product.product_no
        item.product_image = product.image
        item.spec_full_name = spec.spec_full_name
        item.change_quantity(quantity)
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
                try:
                    sku = item.sku_instance
                    sku.change_estimate_quantity(item.quantity_has_count)
                    sku.put()
                except:
                    pass

    def volumetric_weight(self, divisor=6000.0):
        n = self.size_1 * self.size_2 * self.size_3 / float(divisor)
        return n

    @property
    def spec_instance(self):
        if not hasattr(self, '_spec'):
            self._spec = self.spec.get()
        return self._spec

    @property
    def sku_instance(self):
        if not hasattr(self, '_sku'):
            self._sku = self.sku.get()
        return self._sku

    @property
    def product_instance(self):
        if not hasattr(self, '_product'):
            self._product = self.spec_instance.product_object.get()
        return self._product

    def change_quantity(self, quantity):
        spec = self.spec_instance
        product = self.product_instance
        if self.order_type_value == 0:
            config = ConfigModel.get_config()
            if config.stock_recover:
                self.expired_time = time() + config.stock_recover_time
            else:
                self.expired_time = time() + 525600
            can_use_quantity = spec.quantity_can_be_used + int(self.quantity_has_count)
            old_quantity_has_count = self.quantity_has_count
            if can_use_quantity >= quantity and product.can_order:
                self.can_add_to_order = True
                self.quantity = quantity
                self.quantity_has_count = quantity
            else:
                self.can_add_to_order = False
                self.quantity = 0
                self.quantity_has_count = 0
            spec.change_estimate_quantity(sub_quantity=old_quantity_has_count, add_quantity=self.quantity)
            spec.put()
        else:
            if product.can_pre_order:
                self.can_add_to_order = True
                self.quantity = quantity
            else:
                self.can_add_to_order = False
                self.quantity = 0
            spec.change_pre_order_quantity(sub_quantity=int(self.quantity_has_count), add_quantity=self.quantity)
            spec.put()

    def quantity_can_be_order(self, user=None, sku=None):
        if sku is None:
            sku = self.sku.get()
        if self.order_type_value > 0:
            return 999
        if user and self.quantity is not None:
            c = sku.quantity_can_be_used + self.quantity
            if c > 0:
                return c
        return sku.quantity_can_be_used


def get_quantity_with_shopping_car(sku, user=None, *args, **kwargs):
    if user:
        cart_item = ShoppingCartItemModel.get(user, sku)
        if cart_item:
            q = cart_item.quantity_can_be_order(user, sku)
            if q > 0:
                return q
    return sku.quantity_can_be_used
