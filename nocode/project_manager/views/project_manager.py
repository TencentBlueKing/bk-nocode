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
import json

from django.http import FileResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.response import Response

from itsm.component.utils.misc import JsonEncoder
from itsm.project.handler.project_handler import ProjectHandler
from itsm.project.serializers import ProjectSerializer
from nocode.base.base_viewset import BaseApiViewSet
from nocode.project_manager.handlers.operate_handler import OperateLogHandler
from nocode.project_manager.handlers.project_export_handler import ProjectExportHandler
from nocode.project_manager.handlers.project_import_handler import ProjectImportHandler
from nocode.project_manager.handlers.project_manager_handler import (
    ProjectManagerHandler,
)
from nocode.project_manager.handlers.project_version_handler import (
    ProjectVersionModelHandler,
)
from nocode.project_manager.handlers.publish_log_handler import PublishLogModelHandler
from nocode.project_manager.permission import ProjectManagerPermission
from nocode.project_manager.serializers import query
from nocode.project_manager.serializers.project_version import (
    ProjectVersionModelSerializer,
)
from nocode.project_manager.serializers.publish_log import PublishLogModelSerializer

ProjectManagerViewTags = ["project_manager"]


class ProjectManagerViewSet(BaseApiViewSet):
    permission_classes = (ProjectManagerPermission,)

    @swagger_auto_schema(
        operation_summary="应用发布一个新版本",
        tags=ProjectManagerViewTags,
        request_body=query.ProjectPublishSerializer(),
    )
    @action(
        detail=False, methods=["post"], serializer_class=query.ProjectPublishSerializer
    )
    def publish(self, request, *args, **kwargs):
        """"""
        project_key = self.validated_data["project_key"]
        task = ProjectManagerHandler(project_key).create_publish_task()
        instance = ProjectHandler(project_key=project_key).instance
        OperateLogHandler.log_create(
            content=f"{request.user.username} 对应用{instance.name}进行发布:",
            operator=request.user.username,
            project_key=instance.key,
            module=instance.name,
        )
        return Response({"task_id": task.id})

    @swagger_auto_schema(
        operation_summary="查询应用的发布日志",
        tags=ProjectManagerViewTags,
        query_serializer=query.ProjectPublishLogSerializer(),
    )
    @action(
        detail=False,
        methods=["get"],
        serializer_class=query.ProjectPublishLogSerializer,
    )
    def publish_logs(self, request, *args, **kwargs):
        task_id = self.validated_data["task_id"]
        logs = PublishLogModelHandler(task_id=task_id).get_logs()
        serializer = PublishLogModelSerializer(logs, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="获取项目下的版本",
        tags=ProjectManagerViewTags,
        request_body=query.ProjectVersionQuerySerializer(),
    )
    @action(
        detail=False,
        methods=["post"],
        serializer_class=query.ProjectVersionQuerySerializer,
    )
    def version(self, request, *args, **kwargs):
        project_key = self.validated_data["project_key"]
        version_number = self.validated_data["version_number"]

        version = ProjectVersionModelHandler(project_key=project_key).get_version(
            version_number
        )

        serializer = ProjectVersionModelSerializer(version)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="应用导出",
        tags=ProjectManagerViewTags,
    )
    @action(
        detail=False, methods=["get"], serializer_class=query.ProjectPublishSerializer
    )
    def export(self, request, *args, **kwargs):
        project_key = self.validated_data["project_key"]
        data = ProjectExportHandler(project_key).build_tag_data()
        # 统一导入导出格式为列表数据
        response = FileResponse(json.dumps(data, cls=JsonEncoder, indent=2))
        response["Content-Type"] = "application/octet-stream"
        # 中文文件名乱码问题
        response["Content-Disposition"] = "attachment; filename*=UTF-8''{}.json".format(
            project_key
        )

        return response

    @swagger_auto_schema(
        operation_summary="应用导入",
        tags=ProjectManagerViewTags,
    )
    @action(detail=False, methods=["post"])
    def import_project(self, request, *args, **kwargs):
        project_data = request.data
        project_serializer = ProjectSerializer(
            data=project_data, context={"request": request}
        )
        project_serializer.is_valid(raise_exception=True)

        data = json.loads(request.FILES.get("file").read())
        ProjectImportHandler(data, request).import_project(project_serializer)
        return Response()
