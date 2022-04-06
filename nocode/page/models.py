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
import jsonfield
from django.utils.translation import ugettext as _
from django.db import models
from mptt.fields import TreeForeignKey

from nocode.base.base_model import BaseMpttModel, Model
from nocode.base.basic import get_random_key
from nocode.base.constants import (
    LEN_LONG,
    LEN_SHORT,
    LEN_MIDDLE,
    LEN_NORMAL,
    LEN_X_LONG,
    EMPTY_LIST,
    EMPTY_STRING,
    DEFAULT_PROJECT_PROJECT_KEY,
    FIRST_ORDER,
    DISPLAY_CHOICES,
    EMPTY_DICT,
    PAGE_COMPONENT_TYPE_CHOICES,
    PAGE_TYPE_CHOICES,
)


class Page(BaseMpttModel):

    key = models.CharField(verbose_name=_("页面关键字"), max_length=LEN_LONG)
    name = models.CharField(verbose_name=_("页面名称"), max_length=LEN_NORMAL)
    desc = models.CharField(_("页面描述"), max_length=LEN_LONG, null=True, blank=True)
    order = models.IntegerField(verbose_name=_("节点顺序"), default=FIRST_ORDER)
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        verbose_name=_("上级页面"),
        null=True,
        blank=True,
        related_name="children",
    )
    icon = models.CharField(
        verbose_name=_("图标"), null=True, blank=True, max_length=LEN_MIDDLE
    )
    type = models.CharField(
        verbose_name=_("页面类型"), choices=PAGE_TYPE_CHOICES, max_length=LEN_SHORT
    )
    project_key = models.CharField(
        verbose_name=_("项目"),
        max_length=LEN_SHORT,
        null=False,
        default=DEFAULT_PROJECT_PROJECT_KEY,
    )
    route = jsonfield.JSONField(_("前置路径集合"), default=EMPTY_LIST)

    display_type = models.CharField(
        _("可见范围类型"), max_length=LEN_SHORT, choices=DISPLAY_CHOICES, default="OPEN"
    )
    display_role = models.CharField(
        _("可见范围"), max_length=LEN_LONG, default=EMPTY_STRING, null=True, blank=True
    )

    component_list = jsonfield.JSONField(
        verbose_name=_("页面表层组件id列表"), default=EMPTY_LIST
    )

    change_flag = True

    def tag_data(self):
        return {
            "id": self.id,
            "key": self.key,
            "name": self.name,
            "order": self.order,
            "route": self.route,
            "project_key": self.project_key,
            "type": self.type,
            "parent": self.parent,
            "icon": self.icon,
            "desc": self.desc,
            "display_type": self.display_type,
            "display_role": self.display_role,
            "component_list": self.component_list,
        }

    def save(self, *args, **kwargs):
        """自动填充key"""

        # 创建目录时若key为空则自动生成key
        if self.pk is None and not self.key:
            self.key = get_random_key(self.name)

        # get_ancestors不能用于未创建的实例
        if self.parent:
            self.route = list(
                self.parent.get_ancestors(include_self=True).values("id", "name")
            )

        return super(Page, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.project_key}_{self.name}"

    class Meta:
        app_label = "page"
        verbose_name_plural = _("页面")
        verbose_name = _("页面")
        ordering = ("order",)


class PageComponent(Model):

    type = models.CharField(
        verbose_name=_("表单组件/列表组件/功能卡片"),
        choices=PAGE_COMPONENT_TYPE_CHOICES,
        max_length=LEN_SHORT,
    )
    value = models.CharField(verbose_name=_("组件绑定的值"), max_length=LEN_X_LONG)
    layout = models.JSONField(verbose_name=_("组件布局"), default=EMPTY_DICT)
    config = jsonfield.JSONField(verbose_name=_("页面配置"))
    page_id = models.IntegerField(verbose_name=_("页面id"))

    change_flag = True

    def tag_data(self):
        return {
            "id": self.id,
            "type": self.type,
            "value": self.value,
            "layout": self.layout,
            "config": self.config,
            "page_id": self.page_id,
        }

    class Meta:
        app_label = "page"
        verbose_name_plural = _("页面组件")
        verbose_name = _("页面组件")


class PageComponentCollection(models.Model):
    username = models.CharField(_("收藏的用户"), max_length=LEN_LONG)
    component_id = models.IntegerField(_("组件id"))
    page_id = models.IntegerField(_("页面id"), default=0)
    project_key = models.CharField(_("所属应用"), max_length=LEN_MIDDLE)
    create_at = models.DateTimeField(_("收藏时间"), auto_now_add=True)

    class Meta:
        app_label = "page"
        verbose_name_plural = _("组件收藏")
        verbose_name = _("组件收藏")


class PageOpenRecord(models.Model):
    token = models.CharField(_("页面访问token"), max_length=LEN_NORMAL)
    project_key = models.CharField(
        verbose_name=_("项目"),
        max_length=LEN_SHORT,
        null=False,
        default=DEFAULT_PROJECT_PROJECT_KEY,
    )
    page_id = models.IntegerField(verbose_name=_("页面id"))
    service_id = models.IntegerField(verbose_name=_("服务id"))
    config = jsonfield.JSONField(verbose_name=_("页面配置"))
    end_time = models.DateTimeField(_("截止时间"))
