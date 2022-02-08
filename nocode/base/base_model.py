# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-NOCODE SMAKER蓝鲸无代码平台  available.

Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.

BK-NOCODE 蓝鲸无代码平台(S-maker) is licensed under the MIT License.

License for BK-NOCODE 蓝鲸无代码平台(S-maker) :
--------------------------------------------------------------------
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial
portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from django.db import models, transaction
from django.db.models import QuerySet
from django.utils.translation import ugettext as _
from mptt.managers import TreeManager
from mptt.models import MPTTModel

from itsm.component.constants import LEN_NORMAL
from nocode.base import managers


class SoftDeleteQuerySet(QuerySet):
    def delete(self):
        with transaction.atomic():
            return (
                super(SoftDeleteQuerySet, self)
                .select_for_update()
                .update(is_deleted=True)
            )

    def hard_delete(self):
        return super(SoftDeleteQuerySet, self).delete()


class Manager(models.Manager):
    """支持软删除"""

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model).filter(is_deleted=False)


class Model(models.Model):
    """基础字段"""

    FIELDS = ("creator", "create_at", "updated_by", "update_at")

    creator = models.CharField(_("创建人"), max_length=LEN_NORMAL, null=True, blank=True)
    create_at = models.DateTimeField(_("创建时间"), auto_now_add=True)
    update_at = models.DateTimeField(_("更新时间"), auto_now=True)
    updated_by = models.CharField(
        _("修改人"), max_length=LEN_NORMAL, null=True, blank=True
    )
    is_deleted = models.BooleanField(_("是否软删除"), default=False, db_index=True)

    objects = Manager()
    _objects = models.Manager()

    class Meta:
        app_label = "base"
        abstract = True

    def delete(self, using=None):
        self.is_deleted = True
        self.save()

    def hard_delete(self, using=None):
        super(Model, self).delete()


class BaseMpttModel(MPTTModel):
    """基础字段"""

    FIELDS = ("creator", "create_at", "updated_by", "update_at", "end_at")

    creator = models.CharField(
        _("创建人"), max_length=LEN_NORMAL, null=True, blank=True, default="system"
    )
    create_at = models.DateTimeField(_("创建时间"), auto_now_add=True)
    update_at = models.DateTimeField(_("更新时间"), auto_now=True)
    updated_by = models.CharField(
        _("修改人"), max_length=LEN_NORMAL, null=True, blank=True, default="system"
    )
    end_at = models.DateTimeField(_("结束时间"), null=True, blank=True)
    is_deleted = models.BooleanField(_("是否软删除"), default=False, db_index=True)

    _objects = TreeManager()
    objects = managers.DictDataManager()

    class Meta:
        app_label = "service"
        abstract = True

    def delete(self, using=None):
        self.is_deleted = True
        self.save()

    def hard_delete(self, using=None):
        super(BaseMpttModel, self).delete()
