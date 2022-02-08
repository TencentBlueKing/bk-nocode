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
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.response import Response

from nocode.base.base_viewset import BaseApiViewSet
from nocode.project_manager.handlers.project_version_handler import (
    ProjectVersionModelHandler,
)
from nocode.project_manager.permission import (
    ProjectAccessPermission,
    ProjectStatusPermission,
)
from nocode.project_manager.serializers import query

ProjectVersionViewTags = ["project_version"]


class ProjectVersionViewSet(BaseApiViewSet):

    permission_classes = (ProjectAccessPermission, ProjectStatusPermission)

    @swagger_auto_schema(
        operation_summary="获取某个版本的项目配置",
        tags=ProjectVersionViewTags,
        query_serializer=query.ProjectVersionQuerySerializer(),
    )
    @action(
        detail=False,
        methods=["get"],
        serializer_class=query.ProjectVersionQuerySerializer,
    )
    def project_config(self, request, *args, **kwargs):
        project_key = self.validated_data["project_key"]
        version_number = self.validated_data["version_number"]

        project_config = ProjectVersionModelHandler(
            project_key=project_key, version_number=version_number
        ).get_project_config()

        return Response(project_config)

    @swagger_auto_schema(
        operation_summary="获取某个版本的页面导航配置",
        tags=ProjectVersionViewTags,
        query_serializer=query.ProjectVersionQuerySerializer(),
    )
    @action(
        detail=False,
        methods=["get"],
        serializer_class=query.ProjectVersionQuerySerializer,
    )
    def page(self, request, *args, **kwargs):
        project_key = self.validated_data["project_key"]
        version_number = self.validated_data["version_number"]

        page = ProjectVersionModelHandler(
            project_key=project_key, version_number=version_number
        ).get_page()
        return Response(page[0])

    @swagger_auto_schema(
        operation_summary="获取某个版本的页面下的组件配置",
        tags=ProjectVersionViewTags,
        query_serializer=query.PageComponentQuerySerializer(),
    )
    @action(
        detail=False,
        methods=["get"],
        serializer_class=query.PageComponentQuerySerializer,
    )
    def page_component(self, request, *args, **kwargs):
        project_key = self.validated_data["project_key"]
        version_number = self.validated_data["version_number"]
        page_id = self.validated_data["page_id"]

        current_project_version = ProjectVersionModelHandler(
            project_key=project_key, version_number=version_number
        )
        page_component = current_project_version.get_page_component(page_id=page_id)

        return Response(page_component)

    @swagger_auto_schema(
        operation_summary="获取某个版本下的工作表配置",
        tags=ProjectVersionViewTags,
        query_serializer=query.ProjectVersionQuerySerializer(),
    )
    @action(
        detail=False,
        methods=["get"],
        serializer_class=query.ProjectVersionQuerySerializer,
    )
    def worksheet(self, request, *args, **kwargs):
        project_key = self.validated_data["project_key"]
        version_number = self.validated_data["version_number"]

        worksheet = ProjectVersionModelHandler(
            project_key=project_key, version_number=version_number
        ).get_worksheet()

        return Response(worksheet)

    @swagger_auto_schema(
        operation_summary="获取某个版本下的工作表下的字段信息",
        tags=ProjectVersionViewTags,
        query_serializer=query.WorkSheetFieldQuerySerializer(),
    )
    @action(
        detail=False,
        methods=["get"],
        serializer_class=query.WorkSheetFieldQuerySerializer,
    )
    def worksheet_field(self, request, *args, **kwargs):
        project_key = self.validated_data["project_key"]
        version_number = self.validated_data["version_number"]
        worksheet_id = self.validated_data["worksheet_id"]

        worksheet_fields = ProjectVersionModelHandler(
            project_key=project_key, version_number=version_number
        ).get_worksheet_fields(worksheet_id)

        return Response(worksheet_fields)
