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

from nocode.base.constants import TIME_RANGE_BUILTIN
from nocode.data_engine.core.constants import YEARS_APART, MONTH, DAY
from nocode.data_engine.handlers.module_handlers import (
    WorkSheetHandler,
    PageComponentHandler,
)
from nocode.worksheet.models import WorkSheetField


class ListComponentSerializers(serializers.Serializer):
    page_id = serializers.IntegerField(help_text=_("页面id"))
    tab_id = serializers.CharField(
        required=False, help_text=_("列表选项卡id"), max_length=32
    )
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


class ChartComponentDataSerializer(serializers.Serializer):
    chart_configs = serializers.JSONField(required=True, help_text="表格配置")

    def time_range_check(self, config):
        if not config.get("time_range"):
            raise serializers.ValidationError(detail=_("当前为图表组件，请选择时间范围"))
        time_range = config["time_range"]
        expression_time_value = []
        if time_range["type"].upper() not in TIME_RANGE_BUILTIN:
            raise serializers.ValidationError(detail=_("当前为图表组件，请选择时间范围"))
        if time_range["type"].upper() == "DEFINE":
            conditions = time_range.get("conditions")
            if not conditions:
                raise serializers.ValidationError(detail=_("自定义，需提供数据起止时间范围"))
            expression_list = conditions.get("expressions")
            if len(expression_list) != 2 or not expression_list:
                raise serializers.ValidationError(detail=_("当前为图表组件，需提供数据起止时间范围"))
            for expression in expression_list:
                if not expression.get("value"):
                    raise serializers.ValidationError(detail=_("当前为图表组件，需提供数据起止时间范围"))
                expression_time_value.append(expression.get("value"))
        return expression_time_value

    def x_label_check(self, config, expression_time_value):
        x_label = config.get("xaxes")
        time_range = config["time_range"]
        if not x_label:
            raise serializers.ValidationError(detail=_("当前为图表组件，需提供数据统计依据"))
        if x_label.get("type") == "time" and time_range["type"].upper() == "DEFINE":
            value = x_label.get("value")
            if value == DAY:
                expression_year_month = [
                    item.rsplit("-", 1)[0] for item in expression_time_value
                ]
                if expression_year_month[0] != expression_year_month[1]:
                    raise serializers.ValidationError(
                        detail=_("统计类型为时间，且依据分组为天的时候，时间范围只能是某一年同一个月")
                    )

            if value == MONTH:
                expression_year = [
                    int(item.split("-")[0]) for item in expression_time_value
                ]
                if expression_year[0] - expression_year[1] >= YEARS_APART:
                    raise serializers.ValidationError(
                        detail=_("统计类型为时间，且依据分组为月份的时候，时间范围相隔不能超过3年")
                    )

    def y_label_check(self, config):
        y_labels = config.get("yaxis_list")
        if not y_labels:
            raise serializers.ValidationError(detail=_("当前为图表组件，需数据统计依据"))
        for y_label in y_labels:
            if y_label["field"] != "total":
                worksheet_id = config["worksheet_id"]
                field = WorkSheetField.objects.get(
                    key=y_label["field"], is_deleted=False
                )
                if worksheet_id != field.worksheet_id:
                    raise serializers.ValidationError(
                        detail=_(
                            f"当前为图表组件，表单worksheet_id:{worksheet_id} 没有字段field_key:{field.key}"
                        )
                    )

    def base_check(self, config):
        if not config:
            raise serializers.ValidationError(detail=_("当前为图表组件，组件设置不可为空"))
        if not config.get("project_key"):
            raise serializers.ValidationError(detail=_("当前为图表组件，需设置应用"))
        if not config.get("worksheet_id"):
            raise serializers.ValidationError(detail=_("当前为图表组件，需要应用下的表单作为数据源"))
        worksheet = WorkSheetHandler(worksheet_id=config["worksheet_id"]).get_instance()

        # 有数据联动的可能性
        if worksheet.project_key != config["project_key"]:
            raise serializers.ValidationError(detail=_("当前为图表组件，当前表单不属于该应用"))

    def check_chart_config(self, attrs):
        configs = attrs.get("chart_configs")
        for config in configs:
            self.base_check(config)
            # 时间范围
            expression_time_value = self.time_range_check(config)
            # x轴检查
            self.x_label_check(config, expression_time_value)
            # y轴检查
            self.y_label_check(config)

    def validate(self, attrs):
        self.check_chart_config(attrs)
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
    project_key = serializers.CharField(required=True)
