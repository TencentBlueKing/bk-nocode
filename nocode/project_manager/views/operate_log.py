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
from rest_framework.response import Response


from nocode.base.base_viewset import BaseReadOnlyViewSet
from nocode.page.permission import OperateModelPermission
from nocode.project_manager.handlers.operate_handler import OperateLogHandler
from nocode.project_manager.models import OperateLog
from nocode.project_manager.serializers.operate_log import OperateModelSerializer

ProjectVersionViewTags = ["project_operate_log"]


class OperateLogViewSet(BaseReadOnlyViewSet):
    queryset = OperateLog.objects.all().order_by("-create_at")
    serializer_class = OperateModelSerializer
    permission_classes = (OperateModelPermission,)

    filter_fields = {
        "operator": ["exact", "contains", "startswith", "icontains"],
        "module": ["exact", "contains", "startswith", "icontains"],
    }

    @swagger_auto_schema(
        operation_summary="获取该用户可见的日志列表",
        tags=ProjectVersionViewTags,
    )
    def list(self, request, *args, **kwargs):
        """
        获取用户有权限的项目，之后再获取相关的日志
        """
        project_name = request.query_params.get("project_name")
        start_time = request.query_params.get("start_time")
        end_time = request.query_params.get("end_time")

        # 名称过滤
        queryset = self.filter_queryset(self.get_queryset())
        if project_name:
            queryset = OperateLogHandler().filter_project_name(queryset, project_name)
        # 时间过滤
        if start_time and end_time:
            queryset = OperateLogHandler().filter_time(start_time, end_time, queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="查看日志详情",
        tags=ProjectVersionViewTags,
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
