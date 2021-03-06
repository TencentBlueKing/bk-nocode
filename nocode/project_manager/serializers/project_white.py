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

from rest_framework import serializers

from itsm.project.handler.project_handler import ProjectHandler
from nocode.project_manager.models import ProjectWhite
from nocode.worksheet.handlers.worksheet_handler import WorkSheetModelHandler


class ProjectWhiteSerializer(serializers.ModelSerializer):
    projects = serializers.ListField(
        required=True, help_text="授权应用唯一标识列表", write_only=True
    )
    granted_project = serializers.JSONField(required=False)

    def create(self, validated_data):
        project_list = validated_data.pop("projects")
        validated_data["granted_project"] = {"projects": project_list}
        return super(ProjectWhiteSerializer, self).create(validated_data)

    def to_representation(self, instance):
        data = super(ProjectWhiteSerializer, self).to_representation(instance)
        data["granted_project"] = instance.granted_project["projects"]

        # 表单名称
        worksheet = WorkSheetModelHandler(worksheet_id=data["value"]).instance
        data["worksheet_name"] = worksheet.name
        project_handler = ProjectHandler(project_key=data["project_key"])
        data["project_name"] = project_handler.instance.name
        data["granted_project_name"] = project_handler.all_project.filter(
            key__in=instance.granted_project["projects"]
        ).values_list("name", flat=True)
        return data

    class Meta:
        model = ProjectWhite
        fields = (
            "id",
            "value",
            "project_key",
            "projects",
            "type",
            "granted_project",
        ) + model.FIELDS
        read_only_fields = model.FIELDS


class WhiteProjectOperate(serializers.Serializer):
    projects = serializers.ListField(help_text="应用白名单列表")
