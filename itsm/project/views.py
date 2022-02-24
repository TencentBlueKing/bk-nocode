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

# 当前提供给前端获取用户权限链接使用

from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.decorators import action

from itsm.component.constants import MANAGER_CENTER, SHOW_IN_CENTER
from itsm.component.drf import viewsets as component_viewsets
from itsm.component.constants.iam import ACTIONS
from itsm.auth_iam.utils import IamRequest
from itsm.project.handler.module_handler import PageComponentCollectionHandler
from itsm.project.handler.project_handler import ProjectHandler
from itsm.project.models import (
    Project,
    UserProjectAccessRecord,
    ProjectConfig,
)
from itsm.project.permission import ProjectPermission
from itsm.project.serializers import (
    ProjectSerializer,
    ProjectConfigSerializer,
    ProjectMangerSerializer,
)
from nocode.project_manager.permission import SystemUserPermission


class ProjectViewSet(component_viewsets.AuthModelViewSet):
    serializer_class = ProjectSerializer
    queryset = Project.objects.filter(
        ~Q(key__in=["public", "0"]), is_deleted=False
    ).order_by("create_at", "-update_at")

    filter_fields = {
        "name": ["exact", "contains", "startswith", "icontains"],
        "key": ["exact", "in"],
        "publish_status": ["exact", "contains", "startswith", "icontains"],
        # "owner__users": ["exact", "in"],
    }
    permission_classes = (ProjectPermission,)

    def perform_destroy(self, instance):
        PageComponentCollectionHandler(
            project_key=instance.key
        ).delete_collection_history()
        super().perform_destroy(instance)

    def list(self, request, *args, **kwargs):
        need_page = request.query_params.get("need_page", 1)
        if not need_page:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            serializer.context["request"] = request
            return Response(serializer.data)
        return super(ProjectViewSet, self).list(request, *args, **kwargs)

    @action(detail=False, methods=["get"])
    def all(self, request, *args, **kwargs):
        """
        查询当前用户所有项目依赖的权限
        @return: 所有项目的信息以及对应项目下当前用户依赖的权限
        """
        show_type = request.query_params.get("show_type")
        if show_type == MANAGER_CENTER:
            user = request.user
            queryset = self.get_queryset().filter(
                Q(owner__users__icontains=user.username) | Q(creator=user.username)
            )
        else:
            queryset = self.get_queryset().filter(publish_status__in=SHOW_IN_CENTER)

        queryset = self.filter_queryset(queryset)
        serializer = self.get_serializer(queryset, many=True)
        serializer.context["request"] = request
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def info(self, request, *args, **kwargs):
        """查询用户依赖当前项目的权限"""
        iam_client = IamRequest(request)
        apply_actions = []

        project_instance = self.get_object()

        # 默认项目信息
        project_info = {
            "resource_id": project_instance.key,
            "resource_name": project_instance.name,
            "resource_type": "project",
            "resource_type_name": "项目",
        }
        for action_info in ACTIONS:
            if "project" in action_info["relate_resources"]:
                apply_actions.append(action_info["id"])

        auth_actions = iam_client.batch_resource_multi_actions_allowed(
            apply_actions, [project_info]
        ).get("0", {})

        auth_actions = [
            action_id for action_id, result in auth_actions.items() if result
        ]

        project_info["auth_actions"] = auth_actions
        return Response(project_info)

    @action(detail=True, methods=["post"])
    def update_project_record(self, request, *args, **kwargs):
        instance = self.get_object()
        username = request.user.username
        user_project_record = UserProjectAccessRecord.objects.filter(
            username=username
        ).first()
        if user_project_record is None:
            UserProjectAccessRecord.create_record(username, instance.key)
        else:
            user_project_record.update_record(instance.key)

        return Response()

    @swagger_auto_schema(
        operation_summary="应用管理员管理",
    )
    @action(
        detail=False,
        methods=["post"],
        serializer_class=ProjectMangerSerializer,
    )
    def operate_project_manager(self, request, *args, **kwargs):
        serializer = ProjectMangerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        project_handler = ProjectHandler(project_key=validated_data["project_key"])

        username_list = validated_data["users"]
        project_handler.update_owner(username_list)

        return Response(
            data={
                "project_name": project_handler.instance.name,
                "owner": project_handler.instance.owner["users"],
                "project_key": project_handler.instance.key,
            }
        )

    @swagger_auto_schema(
        operation_summary="应用数据管理员管理",
    )
    @action(
        detail=False,
        methods=["post"],
        serializer_class=ProjectMangerSerializer,
    )
    def operate_data_manager(self, request, *args, **kwargs):
        serializer = ProjectMangerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        project_handler = ProjectHandler(project_key=validated_data["project_key"])

        username_list = validated_data["users"]
        project_handler.update_data_owner(username_list)

        return Response(
            data={
                "project_name": project_handler.instance.name,
                "data_owner": project_handler.instance.data_owner["users"],
                "project_key": project_handler.instance.key,
            }
        )

    @swagger_auto_schema(
        operation_summary="应用开发/数据管理员查看",
    )
    @action(detail=False, methods=["get"], permission_classes=[SystemUserPermission])
    def get_project_manager(self, request, *args, **kwargs):
        project_handler = ProjectHandler()
        all_project = project_handler.all_project
        queryset = self.filter_queryset(all_project)
        data = ProjectHandler().get_manager_of_all_projects(queryset)
        return Response(data=data)

    # @action(detail=False, methods=["post"])
    # def migration_project(self, request, *args, **kwargs):
    #     """
    #     request: data
    #     {
    #         "resource_type": "service",
    #         "resource_id":2,
    #         "old_project_key":0,
    #         "new_project_key":"test_project"
    #
    #     }
    #     """
    #     ser = ProjectMigProjectSettingsNotFoundrateSerializer(data=request.data)
    #     ser.is_valid(raise_exception=True)
    #     data = ser.validated_data
    #     MigrationHandlerDispatcher(resource_type=data["resource_type"]).migrate(
    #         data["resource_id"],
    #         data["old_project_key"],
    #         data["new_project_key"],
    #         request,
    #     )
    #
    #     return Response()


class ProjectConfigViewSet(component_viewsets.AuthModelViewSet):
    queryset = ProjectConfig.objects.all()
    serializer_class = ProjectConfigSerializer
