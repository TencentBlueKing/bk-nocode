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

from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings


from nocode.base.base_viewset import BaseApiViewSet
from nocode.data_engine.exceptions import FileValidateError
from nocode.data_engine.handlers.data_handler import (
    ListComponentDataHandler,
    WorkSheetDataHandler,
    ChartDataHandler,
    ListComponentDetailHandler,
    ExportDataHandler,
)
from nocode.data_engine.permission import (
    ListDataAccessPermission,
    ProjectDataPermission,
)
from nocode.data_engine.serializers import query

DataInstanceViewTags = ["data_instance"]


class DataInstanceViewSet(BaseApiViewSet):
    permission_classes = (ListDataAccessPermission,)

    @swagger_auto_schema(
        operation_summary="获取某个列表组件的数据",
        tags=DataInstanceViewTags,
        request_body=query.ListComponentSerializers(),
    )
    @action(
        detail=False, methods=["post"], serializer_class=query.ListComponentSerializers
    )
    def list_component_data(self, request, *args, **kwargs):
        conditions = self.validated_data.get("conditions", {})
        version_number = self.validated_data.get("version_number", None)
        page_id = self.validated_data["page_id"]
        return ListComponentDataHandler(
            page_id, request, version_number
        ).get_list_components_data(conditions)

    @swagger_auto_schema(
        operation_summary="导出某个列表组件的数据",
        tags=DataInstanceViewTags,
        query_serializer=query.ListComponentSerializers(),
    )
    @action(
        detail=False, methods=["post"], serializer_class=query.ListComponentSerializers
    )
    def export_list_component_data(self, request, *args, **kwargs):
        # 没有ids默认获取全部记录
        ids = self.validated_data.get("ids", [])
        conditions = self.validated_data.get("conditions", {})
        page_id = self.validated_data["page_id"]
        version_number = self.validated_data.get("version_number", None)
        return ListComponentDataHandler(
            page_id, request, version_number
        ).export_list_component_data(conditions=conditions, ids=ids)

    @swagger_auto_schema(
        operation_summary="根据筛选条件获取列表的数据",
        tags=DataInstanceViewTags,
        request_body=query.WorkSheetSerializers(),
    )
    @action(
        detail=False,
        methods=["post"],
        serializer_class=query.WorkSheetSerializers,
        permission_classes=[ProjectDataPermission],
    )
    def worksheet_data(self, request, *args, **kwargs):
        token = self.validated_data.get("token")
        if not token:
            return Response()
        data_config_bytes = settings.REDIS_INST.get(token)
        data_config = json.loads(data_config_bytes)

        conditions = self.validated_data.get("conditions", {})
        worksheet_id = data_config["target"]["worksheet_id"]
        fields = self.validated_data["fields"]
        need_page = self.validated_data["need_page"]
        data = WorkSheetDataHandler(worksheet_id, request).data(
            conditions, fields, need_page
        )
        if need_page:
            return data

        return Response(data)

    @swagger_auto_schema(
        operation_summary="获取某个详情按钮的数据",
        tags=DataInstanceViewTags,
        query_serializer=query.DetailSerializers(),
    )
    @action(detail=False, methods=["get"], serializer_class=query.DetailSerializers)
    def get_detail_data(self, request, *args, **kwargs):
        worksheet_id = self.validated_data["worksheet_id"]
        pk = self.validated_data["pk"]
        service_id = self.validated_data["service_id"]
        data = ListComponentDetailHandler(
            service_id=service_id, pk=pk, worksheet_id=worksheet_id
        ).data()
        return Response(data)

    @swagger_auto_schema(
        operation_summary="生成导入模版",
        tags=DataInstanceViewTags,
        query_serializer=query.ListComponentSerializers(),
    )
    @action(
        detail=False, methods=["get"], serializer_class=query.ListComponentSerializers
    )
    def generate_export_template(self, request, *args, **kwargs):
        page_id = self.validated_data["page_id"]
        version_number = self.validated_data["version_number"]
        return ListComponentDataHandler(
            page_id, request, version_number
        ).generate_export_template()

    @swagger_auto_schema(
        operation_summary="获取某个图表页面的数据回馈",
        tags=DataInstanceViewTags,
        request_body=query.ChartComponentDataSerializer(),
    )
    @action(
        detail=False,
        methods=["post"],
        serializer_class=query.ChartComponentDataSerializer,
    )
    def list_chart_data(self, request, *args, **kwargs):
        chart_configs = self.validated_data["chart_configs"]
        data = ChartDataHandler(
            request=request,
        ).analysis(chart_configs)
        return Response(data)

    @swagger_auto_schema(
        operation_summary="导入数据",
        tags=DataInstanceViewTags,
        query_serializer=query.ImportSerializers(),
    )
    @action(detail=False, methods=["post"], serializer_class=query.ImportSerializers)
    def import_data(self, request, *args, **kwargs):
        """
        重复导入的问题
        """
        file = request.FILES.get("file")
        worksheet_id = self.validated_data["worksheet_id"]
        excel_type = file.name.split(".")[1]
        if excel_type not in ["xls", "xlsx"]:
            raise FileValidateError()

        ExportDataHandler(worksheet_id=worksheet_id, request=request).import_by_excels(
            file
        )

        return Response()

    @swagger_auto_schema(
        operation_summary="导入数据校验",
        tags=DataInstanceViewTags,
        query_serializer=query.ImportSerializers(),
    )
    @action(detail=False, methods=["post"], serializer_class=query.ImportSerializers)
    def validate_data(self, request, *args, **kwargs):
        """
        重复导入的问题
        """
        file = request.FILES.get("file")
        worksheet_id = self.validated_data["worksheet_id"]
        excel_type = file.name.split(".")[1]
        if excel_type not in ["xls", "xlsx"]:
            raise FileValidateError()

        results = ExportDataHandler(
            worksheet_id=worksheet_id, request=request
        ).validate(file)

        return Response(results)
