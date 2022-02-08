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
from django.db.models.query import QuerySet
from mptt.managers import TreeManager
from django.db import models, transaction


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


class BaseTreeManager(TreeManager):
    """soft delete: objects.delete()"""

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=False)
        # return SoftDeleteQuerySet(self.model).select_related("parent")


class BaseMpttManager(BaseTreeManager):
    pass


class DictDataManager(BaseMpttManager):
    pass


class PageManager(BaseMpttManager):
    pass


class Manager(models.Manager):
    """支持软删除"""

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model).filter(is_deleted=False)
