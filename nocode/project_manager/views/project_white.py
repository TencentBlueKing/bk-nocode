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
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.response import Response

from itsm.project.handler.project_handler import ProjectHandler
from nocode.base.module_handler import ModelViewSet
from nocode.project_manager.handlers.project_white_handler import (
    ProjectWhiteHandler,
)
from nocode.project_manager.models import ProjectWhite
from nocode.project_manager.permission import WhiteListPermission
from nocode.project_manager.serializers.project_white import (
    ProjectWhiteSerializer,
    WhiteProjectOperate,
)


class ProjectWhiteViewSet(ModelViewSet):
    queryset = ProjectWhite.objects.all()
    serializer_class = ProjectWhiteSerializer
    permission_classes = [WhiteListPermission]
    filter_fields = {
        "value": ["exact", "contains", "startswith", "icontains"],
    }

    @swagger_auto_schema(operation_summary="白名单列表")
    def list(self, request, *args, **kwargs):
        username = request.user.username
        project_list = (
            ProjectHandler()
            .all_project.filter(
                Q(owner__users__icontains=username) | Q(creator=username),
                is_deleted=False,
            )
            .values_list("key", flat=True)
        )
        self.queryset = self.get_queryset().filter(project_key__in=project_list)
        if request.query_params.get("project_key"):
            self.queryset = self.get_queryset().filter(
                project_key=request.query_params.get("project_key")
            )
        return super(ProjectWhiteViewSet, self).list(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="白名单新增")
    def create(self, request, *args, **kwargs):
        return super(ProjectWhiteViewSet, self).create(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="白名单删除")
    def destroy(self, request, *args, **kwargs):
        return super(ProjectWhiteViewSet, self).destroy(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="白名单更新", request_body=WhiteProjectOperate())
    @action(detail=True, methods=["post"])
    def operate_white_list(self, request, *args, **kwargs):
        serializer = WhiteProjectOperate(data=request.data)
        serializer.is_valid(raise_exception=True)
        project_list = serializer.validated_data["projects"]
        ProjectWhiteHandler(instance=self.get_object()).operate_white_project(
            project_list
        )
        return Response()

    @swagger_auto_schema(operation_summary="获取对该应用授权的应用")
    @action(detail=False, methods=["get"])
    def get_project_granted_by(self, request, *args, **kwargs):
        project_key = request.query_params.get("project_key")
        if not project_key:
            return Response()
        data_struct = ProjectWhiteHandler().get_project_granted_by(project_key)
        return Response(data_struct)

    @swagger_auto_schema(operation_summary="获取应用授权的表单")
    @action(detail=False, methods=["get"])
    def get_worksheets(self, request, *args, **kwargs):
        project_key = request.query_params.get("project")
        target_project_key = request.query_params.get("relate_project")
        if not (project_key and target_project_key):
            return Response()
        data_struct = ProjectWhiteHandler().get_worksheets(
            project_key, target_project_key
        )
        return Response(data_struct)
