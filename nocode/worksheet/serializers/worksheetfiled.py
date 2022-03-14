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
import random
import re

from django.utils.translation import ugettext as _

from rest_framework import serializers
from rest_framework.fields import JSONField

from itsm.postman.models import RemoteApi, RemoteApiInstance
from itsm.postman.serializers import ApiInstanceSerializer
from itsm.project.handler.project_handler import ProjectHandler
from nocode.base.basic import check_user_owner_creator
from nocode.base.constants import CUSTOM, FORMULA, WORKSHEET, CALCULATE_LIMIT
from nocode.project_manager.handlers.project_white_handler import ProjectWhiteHandler
from nocode.worksheet.handlers.worksheet_field_handler import WorkSheetFieldIndexHandler
from nocode.worksheet.models import WorkSheetField, WorkSheet
from nocode.worksheet.serializers import mock_data

var = "^[\u4E00-\u9FA5A-Za-z0-9]+$"

pattern = re.compile(var)


class WorkSheetFieldSerializer(serializers.ModelSerializer):
    regex_config = JSONField(required=False, initial={})
    meta = JSONField(required=False, initial={})
    api_info = JSONField(required=False)
    choice = JSONField(required=False, initial=[])
    kv_relation = JSONField(required=False, initial={})
    num_range = JSONField(required=False)

    def validate_worksheet_id(self, worksheet_id):
        try:
            WorkSheet.objects.get(id=worksheet_id)
        except WorkSheet.DoesNotExist:
            raise serializers.ValidationError(detail=_("对应的工作表不存在！"))

        return worksheet_id

    def validated_data_config(self, data_config):
        """
        表单白名单校验
        """
        source = data_config["source"]
        target = data_config["target"]
        user = self.context["request"].user
        # 同一应用
        if source["project_key"] == target["project_key"]:
            project = ProjectHandler(project_key=target["project_key"]).instance
            same_project_flag = check_user_owner_creator(user=user, project=project)
            if not same_project_flag:
                raise serializers.ValidationError(
                    f"user: {user} 非应用{project.name} 的应用管理员"
                )
        elif source["project_key"] != target["project_key"]:
            # 不同应用
            project = ProjectHandler(project_key=source["project_key"]).instance
            project_flag = check_user_owner_creator(user=user, project=project)
            if not project_flag:
                raise serializers.ValidationError(
                    f"user: {user} 非应用{project.name} 的应用管理员"
                )

            white_flag = ProjectWhiteHandler(
                value=target["worksheet_id"], value_type=WORKSHEET
            ).is_project_in_white_list(source["project_key"])
            if not white_flag:
                raise serializers.ValidationError(
                    "应用{}不在表单worksheet_id:{}的白名单中，请先添加白名单".format(
                        project.name, target["worksheet_id"]
                    )
                )

    def validate(self, attrs):
        if "data_config" in attrs["meta"]:
            self.validated_data_config(attrs["meta"]["data_config"])
        attrs = self.to_api_internal_value(attrs)
        return attrs

    def create(self, validated_data):
        validated_data["key"] = WorkSheetFieldIndexHandler.generate_key()
        WorkSheetFieldIndexHandler.is_support_unique_index(validated_data)
        return super(WorkSheetFieldSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        # 如果之前不是唯一性索引，修改成为唯一性索引，则创建
        if not instance.unique and validated_data["unique"]:
            WorkSheetFieldIndexHandler.is_support_unique_index(validated_data)
        return super(WorkSheetFieldSerializer, self).update(validated_data, instance)

    def to_representation(self, instance):
        data = super(WorkSheetFieldSerializer, self).to_representation(instance)

        if instance.source_type == "API" and instance.api_instance_id:
            api_instance = RemoteApiInstance.objects.filter(id=instance.api_instance_id)
            if not api_instance.exists():
                raise serializers.ValidationError("绑定的api异常")
            data["api_info"] = ApiInstanceSerializer(api_instance[0]).data
        return data

    def get_related_fields(self, api_instance, validated_data):
        """获取当前字段依赖的字段"""
        return {"rely_on": []}

    def to_api_internal_value(self, attrs):
        """
        api字段接口信息格式化
        """
        from itsm.postman.serializers import RemoteApiSerializer

        api_info = attrs.pop("api_info", {})
        if not api_info:
            return attrs

        # 編輯保存
        if api_info.get("remote_api_info"):
            # api數據源沒有變更
            return attrs

        # 新增保存
        api_info.pop("id", "")
        remote_api = RemoteApi.objects.get(id=api_info["remote_api_id"])
        api_info.update(
            remote_api=remote_api,
            remote_api_info=RemoteApiSerializer(remote_api).data,
            map_code=remote_api.map_code,
            before_req=remote_api.before_req,
        )
        """
        {
            "remote_api_id": 12,
            "remote_system_id": 4,
            "req_body": {},
            "req_params": {
                "type": ""
            },
            "rsp_data": "data"
        }
        """
        api_info.pop("remote_system_id")

        api_instance = RemoteApiInstance.objects.create(**api_info)
        attrs["api_instance_id"] = api_instance.id
        # validated_data["related_fields"] = self.get_related_fields(
        #     api_instance, validated_data
        # )
        return attrs

    class Meta:
        model = WorkSheetField
        fields = "__all__"
        # 只读字段在创建和更新时均被忽略
        read_only_fields = ("creator", "create_at", "update_at", "update_by")
        swagger_schema_fields = {"example": mock_data.CREATE_WORK_SHEET_FIELD}


class WorkSheetFieldListSerializer(serializers.Serializer):
    worksheet_id = serializers.IntegerField(help_text=_("工作表id"))

    def validate_worksheet_id(self, worksheet_id):
        try:
            WorkSheet.objects.get(id=worksheet_id)
        except WorkSheet.DoesNotExist:
            raise serializers.ValidationError(detail=_("对应的工作表不存在！"))

        return worksheet_id

    class Meta:
        swagger_schema_fields = {"example": {"worksheet_id": 1}}


class WorkSheetFieldItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, default=None)
    key = serializers.CharField(required=False, default=None)
    meta = serializers.JSONField(required=False, initial={})
    api_info = serializers.JSONField(required=False, initial={})
    choice = serializers.JSONField(required=False, initial=[])
    kv_relation = serializers.JSONField(required=False, initial={})
    related_fields = serializers.JSONField(required=False, initial={})
    regex_config = serializers.JSONField(required=False, initial={})
    unique = serializers.BooleanField(required=False, default=False)
    type = serializers.CharField(required=True)
    num_range = serializers.JSONField(required=False)

    def validated_formula(self, formula, fields_key_list):
        """
        校验公式有效性
        """
        params_dict = {}
        for params_key in fields_key_list:
            params_dict[params_key] = random.randint(1, 9)
        try:
            formula.format_map(params_dict)
        except SyntaxError or Exception:
            raise serializers.ValidationError(_("请输入正确的数学公式"))

    def validated_formula_config(self, attrs):
        """
        计算控件配置校验
        """
        config = attrs["meta"].get("config")
        if not config:
            raise serializers.ValidationError(_("计算控件需设置相应配置"))
        if not config.get("type"):
            raise serializers.ValidationError(_("计算控件需设置计算方法"))

        # 数值计算
        if not config.get("fields") and config.get("calculate_type") == "number":
            raise serializers.ValidationError(_("计算控件需绑定数值"))

        # 使用内置计算计算方法,需要两个字段
        at_least_method = ["PRODUCT", "SUM"]
        if (
            config["type"] in at_least_method
            and len(config["fields"]) <= CALCULATE_LIMIT
        ):
            raise serializers.ValidationError(_("使用内置求和，乘积方法需要至少绑定2个数值控件，可考虑自定义公式"))

        # 验证公式绑定字段类型
        num_fields_type = WorkSheetField.objects.filter(
            key__in=config.get("fields")
        ).values_list("type", flat=True)
        for field_type in num_fields_type:
            if field_type not in ["INT", "DATE"]:
                raise serializers.ValidationError(_("请绑定数值控件或者日期控件"))

        # 数字计算自定义公式校验
        if config.get("type") == CUSTOM and config.get("calculate_type") == "number":
            formula = config.get("value")
            if not formula:
                raise serializers.ValidationError(_("请输入自定义公式"))
            self.validated_formula(
                formula=formula, fields_key_list=config.get("fields")
            )

    def validate(self, attrs):
        if attrs.get("type") == FORMULA:
            self.validated_formula_config(attrs)

        if attrs.get("type") in ["CHECKBOX", "MULTISELECT", "TREESELECT"]:
            num_range = attrs.get("num_range")
            if not isinstance(num_range, list):
                raise serializers.ValidationError(_("字段范围格式不正确"))
            # 如果传了num_range 但是数量等于不是两个
            if num_range:
                if len(num_range) != 2:
                    raise serializers.ValidationError(_("字段范围格式不正确"))
                if num_range[0] == num_range[1]:
                    raise serializers.ValidationError(_("最小范围和最大范围不能相同"))
                if num_range[0] >= num_range[1]:
                    raise serializers.ValidationError(_("最小范围和最大范围设置错误"))
        return attrs

    class Meta:
        model = WorkSheetField
        fields = "__all__"
        # 只读字段在创建和更新时均被忽略
        read_only_fields = ("creator", "create_at", "update_at", "update_by")
        swagger_schema_fields = {"example": mock_data.CREATE_WORK_SHEET_FIELD}


class BatchWorkSheetFieldSerializer(serializers.Serializer):
    worksheet_id = serializers.CharField(help_text=_("批量保存的表单"), required=True)
    fields = serializers.ListField(
        help_text=_("批量保存的字段列表"), child=WorkSheetFieldItemSerializer(), min_length=0
    )
