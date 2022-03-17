# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.

Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.

BK-ITSM 蓝鲸流程服务 is licensed under the MIT License.

License for BK-ITSM 蓝鲸流程服务:
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

import copy
import json
import re
from datetime import datetime

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from django.utils.translation import ugettext as _

from itsm.auth_iam.utils import IamRequest
from itsm.component.constants import (
    CATALOG,
    OPERATE_CATALOG,
    DEFAULT_PROJECT_CONFIG,
    EMPTY_DICT,
)
from itsm.project.handler.permit_engine_handler import PermitInitManagerDispatcher
from itsm.project.handler.project_handler import ProjectHandler, ProjectConfigHandler
from itsm.project.handler.utils import change_so_project_change
from itsm.project.models import Project, ProjectSettings, ProjectConfig
from nocode.page.handlers.page_handler import PageModelHandler

project_name_pattern = re.compile("^[0-9a-zA-Z_-]{1,}$")
workflow_prefix_pattern = re.compile(r"^[A-Za-z]+$")


class ProjectConfigSerializer(serializers.ModelSerializer):
    def validate_workflow_prefix(self, workflow_prefix):
        # 前缀判断
        if not workflow_prefix_pattern.search(workflow_prefix):
            raise serializers.ValidationError("创建失败: 流程前缀只允许英文字母")
        return workflow_prefix

    class Meta:
        model = ProjectConfig
        fields = "__all__"


class ProjectSerializer(ModelSerializer):
    color = serializers.ListField(required=False)
    project_config = serializers.JSONField(
        required=False, help_text="应用设置", write_only=True
    )
    owner = serializers.JSONField(required=False)
    data_owner = serializers.JSONField(required=False)

    def validate_project(self, attrs):
        """
        检验项目名是否符合规范
        """
        if Project.objects.filter(name=attrs["name"], is_deleted=False).exists():
            raise serializers.ValidationError(
                "创建失败: 已存在项目名称为{}的项目".format(attrs["name"])
            )

        project_key = attrs.get("key", "")
        if not project_key:
            raise serializers.ValidationError("应用标识不可为空字符串")
        if len(project_key) > 0:
            if not project_key[0].isalpha():
                raise serializers.ValidationError("应用标识只允许英文字母开头")
            if Project.objects.filter(key=project_key, is_deleted=False).exists():
                raise serializers.ValidationError("应用标识已被使用")
        if not project_name_pattern.search(project_key):
            raise serializers.ValidationError("创建失败: 应用标识只允许包含数字，英文字母, 英文横线- 和下划线_")

    def validated_project_config(self, project_config):
        config_serializers = ProjectConfigSerializer(data=project_config)
        config_serializers.is_valid(raise_exception=True)
        return config_serializers.validated_data

    def create(self, validated_data):
        """改写post方法,提供update_or_create逻辑"""
        self.validate_project(validated_data)
        validated_config = None
        # 校验项目设置
        project_config = validated_data.pop("project_config", EMPTY_DICT)
        if project_config.get("workflow_prefix"):
            validated_config = self.validated_project_config(project_config)

        if validated_data.get("color"):
            validated_data["color"] = json.dumps(validated_data["color"])
        instance = super(ProjectSerializer, self).create(validated_data)

        # 初始化负责人为创建者
        owner = validated_data.get("owner", [instance.creator])
        instance.owner = {"users": owner}
        # 格式化数据管理员
        instance.data_owner = {"users": []}
        instance.save()

        # 创建应用，连带应用设置
        if validated_config:
            ProjectConfigHandler().init_project_config(
                project_key=instance.key, config=validated_config
            )
        else:
            ProjectConfigHandler().init_project_config(
                project_key=instance.key, config=DEFAULT_PROJECT_CONFIG
            )

        catalogs = copy.deepcopy(CATALOG)
        for catalog in catalogs:
            catalog["key"] = "{}_{}".format(instance.key, catalog["key"])
            catalog["parent_key"] = "{}_{}".format(instance.key, catalog["parent_key"])

        # no_code init
        # 创建根目录
        PageModelHandler().create_root(project_key=instance.key)
        # 初始化项目操作目录
        ProjectHandler(instance=instance).init_operate_catalogs(OPERATE_CATALOG)
        handler = ProjectHandler(instance=instance)
        # 创建项目用户组
        handler.init_user_group(
            username=self.context["request"].user.username,
        )

        manager = PermitInitManagerDispatcher(instance=instance)
        manager.init_permit()

        # instance.init_service_catalogs(catalogs)
        # instance.init_project_settings()
        # instance.init_project_sla()
        return instance

    def update(self, instance, validated_data):
        if validated_data.get("color"):
            validated_data["color"] = json.dumps(validated_data["color"])
        project_config = validated_data.pop("project_config")

        if validated_data.get("app_code") or validated_data.get("app_secret"):
            raise serializers.ValidationError("app_secret/app_code 禁止修改")

        # 项目的key不可修改
        if validated_data.get("key") != instance.key:
            raise serializers.ValidationError("更新失败: 项目唯一标识不可修改")

        if project_config:
            validated_config = self.validated_project_config(project_config)
            validated_config["update_at"] = datetime.now()
            config_object = ProjectConfig.objects.get(project_key=instance.key)
            for key, value in validated_config.items():
                if hasattr(config_object, key):
                    setattr(config_object, key, value)
            config_object.save()
        # 数据兼容
        validated_data["owner"] = {
            "users": validated_data.get("owner")
            or instance.owner.get("users", [instance.creator])
        }
        validated_data["data_owner"] = {
            "users": validated_data.get("data_owner")
            or instance.data_owner.get("users", [])
        }
        instance = super(ProjectSerializer, self).update(instance, validated_data)
        change_so_project_change(instance.key)
        return instance

    def to_representation(self, instance):
        data = super(ProjectSerializer, self).to_representation(instance)
        try:
            config_instance = ProjectConfig.objects.get(project_key=instance.key)
            serializer = ProjectConfigSerializer(config_instance)
            data["project_config"] = serializer.data

        except ProjectConfig.DoesNotExist:
            data["project_config"] = {}
        data["owner"] = data["owner"].get("users", [])
        if isinstance(data["data_owner"], list):
            instance.data_owner = {"users": data["data_owner"]}
            instance.save()
            data["data_owner"] = instance.data_owner
        data["data_owner"] = data["data_owner"].get("users", [])
        return self.update_auth_actions(instance, data)

    def update_auth_actions(self, instance, data):
        """
        更新权限信息
        """
        # 默认项目信息
        request = self.context["request"]

        iam_client = IamRequest(request)

        project_info = {
            "resource_id": instance.key,
            "resource_name": instance.name,
            "resource_type": "project",
            "resource_type_name": "项目",
        }
        if hasattr(self.Meta.model, "resource_operations"):
            apply_actions = self.Meta.model.resource_operations
            auth_actions = iam_client.batch_resource_multi_actions_allowed(
                apply_actions, [project_info], project_key=instance.key
            ).get(instance.key, {})
            auth_actions = [
                action_id for action_id, result in auth_actions.items() if result
            ]
            data["auth_actions"] = auth_actions

        if data.get("color"):
            try:
                color_list = json.loads(instance.color)
                data["color"] = color_list
            except Exception:
                color_list = [instance.color]
                data["color"] = color_list
        return data

    class Meta:
        model = Project
        fields = (
            "name",
            "desc",
            "key",
            "logo",
            "color",
            "publish_status",
            "publish_time",
            "project_config",
            "owner",
            "data_owner",
        ) + model.FIELDS
        read_only_fields = model.FIELDS


class ProjectSettingSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)
    type = serializers.CharField(required=True, max_length=32)
    key = serializers.CharField(required=True, max_length=32)
    value = serializers.CharField(required=True, max_length=32)
    project_key = serializers.CharField(
        required=True, max_length=32, source="project_id"
    )
    project = ProjectSerializer(required=False)

    class Meta:
        model = ProjectSettings
        fields = "__all__"


class ProjectMigrateSerializer(serializers.Serializer):
    # 迁移类型
    CHOICES = [
        ("service", "服务"),
        ("user_group", "用户组"),
    ]

    resource_type = serializers.ChoiceField(choices=CHOICES, required=True)
    resource_id = serializers.IntegerField(required=True)
    old_project_key = serializers.CharField(required=True)
    new_project_key = serializers.CharField(required=True)


class ProjectMangerSerializer(serializers.Serializer):
    users = serializers.ListField(required=True, help_text="用户名")
    project_key = serializers.CharField(required=True, help_text="项目唯一标识")

    def validate(self, attrs):
        project_key = attrs["project_key"]

        project = ProjectHandler(project_key)
        if not project.exist:
            raise serializers.ValidationError(detail=_("对应的项目不存在！"))
        return attrs
