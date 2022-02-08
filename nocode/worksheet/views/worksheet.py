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
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from nocode.base.base_permission import PageDesignPermission
from nocode.worksheet.handlers.moudule_handler import BaseModelViewSet
from nocode.worksheet.handlers.worksheet_handler import (
    WorkSheetModelHandler,
    InitWorksheetHandler,
)
from nocode.worksheet.models import WorkSheet
from nocode.worksheet.serializers import worksheet
from nocode.worksheet.serializers.worksheet import (
    WorkSheetSerializer,
    PKWorkSheetSerializer,
)

WorkSheetViewTags = ["worksheet"]


class WorkSheetViewSet(BaseModelViewSet):
    queryset = WorkSheet.objects.all()
    serializer_class = WorkSheetSerializer
    permission_classes = (PageDesignPermission,)

    filter_fields = {
        "name": ["exact", "contains", "startswith", "icontains"],
    }

    def perform_destroy(self, instance):
        """
        如果该目录关联了服务，则无法删除
        """
        WorkSheetModelHandler(instance.id).delete_service()
        super().perform_destroy(instance)

    @swagger_auto_schema(
        operation_summary="工作表列表",
        tags=WorkSheetViewTags,
        query_serializer=worksheet.WorkSheetListSerializer(),
    )
    def list(self, request, *args, **kwargs):
        project_key = self.request.query_params.get("project_key")
        if project_key is not None:
            self.serializer_class = worksheet.WorkSheetListSerializer
            project_key = self.validated_data["project_key"]
            self.queryset = self.filter_queryset(
                self.queryset.filter(project_key=project_key)
            )
            self.serializer_class = WorkSheetSerializer
            return super().list(request, *args, **kwargs)
        return Response()

    @swagger_auto_schema(
        operation_summary="工作表详情",
        tags=WorkSheetViewTags,
        query_serializer=PKWorkSheetSerializer(),
        responses={status.HTTP_200_OK: WorkSheetSerializer()},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="表单关联的服务以及页面",
        tags=WorkSheetViewTags,
    )
    @action(
        detail=True,
        methods=["get"],
    )
    def get_relate_service_page(self, request, *args, **kwargs):
        worksheet_obj = self.get_object()
        data = WorkSheetModelHandler().get_worksheet_relate_service_page(worksheet_obj)
        return Response(data)

    @swagger_auto_schema(
        operation_summary="从excel创建表单",
        tags=WorkSheetViewTags,
    )
    @action(
        detail=False,
        methods=["post"],
    )
    def get_fields_from_excel(self, request, *args, **kwargs):
        file = request.FILES.get("file")
        sheet_name = request.data.get("sheet_name")
        field_details = InitWorksheetHandler(file, sheet_name).get_init_filed_details()
        return Response(field_details)
