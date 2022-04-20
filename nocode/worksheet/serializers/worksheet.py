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
import re
from typing import AnyStr

from django.db import transaction
from django.utils.translation import ugettext as _
from pypinyin import lazy_pinyin

from rest_framework import serializers

from common.log import logger
from nocode.utils.worksheet_tool import ServiceMigrate
from nocode.worksheet.exceptions import CreateWorkSheetError
from nocode.worksheet.handlers.moudule_handler import (
    ProjectHandler,
    DjangoHandler,
    ServiceHandler,
)
from nocode.worksheet.models import WorkSheet
from nocode.worksheet.serializers import mock_data

var = "^[\u4E00-\u9FA5A-Za-z0-9]+$"

pattern = re.compile(var)


class WorkSheetSerializer(serializers.ModelSerializer):
    def validate_project_key(self, project_key: AnyStr) -> AnyStr:
        if not ProjectHandler(project_key).exist():
            raise serializers.ValidationError(detail=_("对应的项目不存在！"))

        return project_key

    def validate_name(self, name):
        if pattern.match(name) is None:
            raise serializers.ValidationError(detail=_("字段名称支持中文英文数字!"))
        if len(name) > 8:
            raise serializers.ValidationError(detail=_("字段名超过最大长度：8"))
        return name

    def create_validate(self, project_key, key):
        if WorkSheet.objects.filter(project_key=project_key, key=key).exists():
            raise serializers.ValidationError(
                detail=_("创建失败,该项目下已经有为该key的工作表!, 请换个工作表名称再试")
            )

    def generate_key(self, validated_data):
        name = validated_data["name"]
        project_key = validated_data["project_key"]

        key = "_".join(lazy_pinyin(name))

        # 如果数据库中已经存在同名的key，则走版本控制
        if WorkSheet._objects.filter(key=key, project_key=project_key).exists():
            # 目前的业务场景，99足够用了
            for version in range(1, 99):
                new_key = "{0}_{1}".format(key, version)
                if not WorkSheet._objects.filter(
                    key=new_key, project_key=project_key
                ).exists():
                    return new_key

        return key

    def update(self, instance, validated_data):
        if "name" in validated_data:
            ServiceMigrate(instance.id).migrate_service_name(validated_data["name"])
        return super(WorkSheetSerializer, self).update(instance, validated_data)

    def create(self, validated_data):
        project_key = validated_data["project_key"]

        key = self.generate_key(validated_data)

        validated_data["key"] = key

        self.create_validate(project_key, key)

        with transaction.atomic():
            instance = super().create(validated_data)
            ServiceHandler(instance).init_service()

        db_name = "{0}_{1}".format(project_key, instance.key)

        try:
            DjangoHandler(db_name).init_db()
        except Exception:
            logger.info(
                "[WorkSheetSerializer]->[create] 工作表初始化失败，project_key={0},key={1}".format(
                    project_key, instance.key
                )
            )
            raise CreateWorkSheetError()
        return instance

    class Meta:
        model = WorkSheet
        fields = "__all__"
        # 只读字段在创建和更新时均被忽略
        read_only_fields = ("creator", "create_at", "update_at", "updated_by", "key")
        swagger_schema_fields = {"example": mock_data.CREATE_WORK_SHEET}


class PKWorkSheetSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {"pk": 1}


class WorkSheetListSerializer(serializers.Serializer):
    project_key = serializers.CharField(help_text=_("应用唯一标识"))

    def validate_project_key(self, project_key):
        if not ProjectHandler(project_key).exist():
            raise serializers.ValidationError(detail=_("对应的项目不存在！"))
        return project_key

    class Meta:
        swagger_schema_fields = {"example": {"project_key": 0}}
