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
from django.db import models

from itsm.postman.models import RemoteApiInstance
from nocode.base.base_model import Model
from nocode.base.constants import (
    LEN_MIDDLE,
    LEN_LONG,
    EMPTY_STRING,
    LEN_SHORT,
    LEN_NORMAL,
    TYPE_CHOICES,
    LAYOUT_CHOICES,
    VALIDATE_CHOICES,
    SOURCE_CHOICES,
    EMPTY_DICT,
    LEN_XX_LONG,
    EMPTY_LIST,
)
from django.utils.translation import ugettext as _


class WorkSheet(Model):
    name = models.CharField(_("工作表名称"), max_length=LEN_MIDDLE)
    desc = models.CharField(
        _("工作表描述"), max_length=LEN_LONG, null=True, blank=True, default=EMPTY_STRING
    )
    key = models.CharField(
        _("工作表标识"), max_length=LEN_SHORT, null=True, blank=True, default=EMPTY_STRING
    )
    project_key = models.CharField(
        _("项目key"), max_length=LEN_SHORT, null=False, default=0
    )
    fields = models.JSONField(_("字段的顺序, 按列表"), default=EMPTY_LIST)

    change_flag = True

    def tag_data(self):
        return {
            "id": self.id,
            "name": self.name,
            "desc": self.desc,
            "key": self.key,
            "project_key": self.project_key,
        }

    class Meta:
        app_label = "worksheet"


class WorkSheetField(Model):
    key = models.CharField(_("字段标识"), max_length=LEN_LONG)
    name = models.CharField(_("字段名"), max_length=LEN_NORMAL)
    desc = models.CharField(
        _("字段填写说明"), max_length=LEN_LONG, default=EMPTY_STRING, null=True, blank=True
    )
    type = models.CharField(
        _("字段类型"), max_length=LEN_SHORT, choices=TYPE_CHOICES, default="STRING"
    )
    layout = models.CharField(
        _("布局"), max_length=LEN_SHORT, choices=LAYOUT_CHOICES, default="COL_6"
    )
    unique = models.BooleanField(_("是否唯一"), default=False, db_index=True)
    validate_type = models.CharField(
        _("校验规则"), max_length=LEN_SHORT, choices=VALIDATE_CHOICES, default="REQUIRE"
    )

    source_type = models.CharField(
        _("数据来源类型"), max_length=LEN_SHORT, choices=SOURCE_CHOICES, default="CUSTOM"
    )
    api_instance_id = models.IntegerField(
        _("api实例主键"), default=0, null=True, blank=True
    )
    kv_relation = jsonfield.JSONCharField(
        _("源数据的kv关系配置"), default=EMPTY_DICT, max_length=LEN_NORMAL
    )
    default = models.CharField(
        _("默认值"), max_length=LEN_XX_LONG, default=EMPTY_STRING, null=True, blank=True
    )
    choice = jsonfield.JSONField(_("选项"), default=EMPTY_LIST)
    meta = jsonfield.JSONField(_("复杂描述信息"), default=EMPTY_DICT)
    worksheet_id = models.IntegerField(_("工作表id"))
    regex = models.CharField(
        _("正则校验规则关键字"),
        max_length=LEN_NORMAL,
        default=EMPTY_STRING,
        null=True,
        blank=True,
    )
    tips = models.CharField(
        _("字段展示说明"), max_length=LEN_MIDDLE, default=EMPTY_STRING, null=True, blank=True
    )

    change_flag = True

    @property
    def api_info(self):
        if self.source_type == "API":
            api_instance_info = RemoteApiInstance.objects.get(
                id=self.api_instance_id
            ).tag_data()
            return api_instance_info
        else:
            return {}

    def tag_data(self):
        return {
            "id": self.id,
            "name": self.name,
            "desc": self.desc,
            "key": self.key,
            "type": self.type,
            "layout": self.layout,
            "unique": self.unique,
            "validate_type": self.validate_type,
            "source_type": self.source_type,
            "api_instance_id": self.api_instance_id,
            "kv_relation": self.kv_relation,
            "default": self.default,
            "choice": self.choice,
            "meta": self.meta,
            "worksheet_id": self.worksheet_id,
            "regex": self.regex,
            "tips": self.tips,
            "api_info": self.api_info,
        }

    class Meta:
        app_label = "worksheet"
