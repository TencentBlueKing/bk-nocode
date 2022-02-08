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
from django.utils.translation import ugettext as _

from rest_framework import serializers

from nocode.data_engine.handlers.module_handlers import (
    WorkSheetHandler,
    PageComponentHandler,
)


class ListComponentSerializers(serializers.Serializer):
    page_id = serializers.IntegerField(help_text=_("页面id"))
    conditions = serializers.JSONField(help_text=_("查询参数"), required=False)
    version_number = serializers.CharField(help_text=_("项目版本"))
    ids = serializers.ListField(help_text=_("批量记录id"), required=False)

    def validate(self, attrs):
        page_id = attrs["page_id"]
        version_number = attrs["version_number"]
        if not PageComponentHandler.exists(page_id, version_number):
            raise serializers.ValidationError("当前应用版本下没有page_id={}的页面".format(page_id))
        return attrs

    class Meta:
        swagger_schema_fields = {"example": {"page_component_id": 1}}


class ChartComponentSerializers(serializers.Serializer):
    page_id = serializers.IntegerField(help_text=_("图表页面id"))
    page_component_id = serializers.IntegerField(help_text=_("图表页面组件id"))
    version_number = serializers.CharField(help_text=_("项目版本"))

    def validate(self, attrs):
        page_id = attrs["page_id"]
        version_number = attrs["version_number"]
        if not PageComponentHandler.exists(page_id, version_number):
            raise serializers.ValidationError("当前应用版本下没有page_id={}的页面".format(page_id))
        return attrs


class WorkSheetBaseSerializers(serializers.Serializer):
    worksheet_id = serializers.IntegerField(help_text=_("工作表ID"))

    def validate_worksheet_id(self, worksheet_id):
        try:
            WorkSheetHandler(worksheet_id).get_instance()
        except Exception:
            raise serializers.ValidationError(
                detail="id={0}对应的工作表不存在".format(worksheet_id)
            )
        return worksheet_id


class WorkSheetSerializers(serializers.Serializer):
    token = serializers.CharField(help_text=_("鉴权参数"))
    conditions = serializers.JSONField(help_text=_("查询参数"), required=False, default={})
    fields = serializers.ListField(help_text=_("字段列表"), required=False, default=[])
    need_page = serializers.BooleanField(
        help_text=_("是否分页"), required=False, default=False
    )


class DetailSerializers(WorkSheetBaseSerializers):
    pk = serializers.IntegerField(help_text=_("数据id"), required=True)
    service_id = serializers.IntegerField(help_text=_("服务id"), required=True)


class ImportSerializers(WorkSheetBaseSerializers):
    pass


class WorkSheetVersionSerializers(WorkSheetBaseSerializers):
    version_number = serializers.CharField(help_text=_("项目版本"))

    def validate(self, attrs):
        worksheet_id = attrs["worksheet_id"]
        version_number = attrs["version_number"]
        if not WorkSheetHandler.exists(worksheet_id, version_number):
            raise serializers.ValidationError(
                "当前应用版本下没有worksheet_id={}的自定义表单".format(worksheet_id)
            )
        return attrs
