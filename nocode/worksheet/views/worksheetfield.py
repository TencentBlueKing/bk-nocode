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

from nocode.base.constants import FORMULA_BUILTIN
from nocode.worksheet.exceptions import DropUniqueIndexError
from nocode.worksheet.handlers.moudule_handler import (
    BaseFieldViewSet,
    DataMangerHandler,
)
from nocode.worksheet.handlers.worksheet_field_handler import (
    WorkSheetFieldBatchModelHandler,
)
from nocode.worksheet.models import WorkSheetField
from nocode.worksheet.permission import WorkSheetFieldPermission
from nocode.worksheet.serializers import worksheetfiled
from nocode.worksheet.serializers.worksheetfiled import (
    WorkSheetFieldSerializer,
    BatchWorkSheetFieldSerializer,
)

WorkSheetFieldViewTags = ["worksheet"]


class WorkSheetFieldViewSet(BaseFieldViewSet):
    queryset = WorkSheetField.objects.all()
    serializer_class = WorkSheetFieldSerializer
    permission_classes = (WorkSheetFieldPermission,)

    filter_fields = {
        "id": ["in"],
        "key": ["exact", "in", "contains", "startswith"],
        "name": ["exact", "contains", "startswith"],
        "type": ["exact", "in"],
        "layout": ["exact", "in"],
        "validate_type": ["exact", "in"],
    }

    def get_queryset(self):
        if not self.request.query_params.get("page_size"):
            self.pagination_class = None
        query_set = super(WorkSheetFieldViewSet, self).get_queryset()
        return query_set

    def perform_destroy(self, instance):
        # 从开始节点出来的连线只能由一条, 且不能被删除
        try:
            DataMangerHandler(worksheet_id=instance.worksheet_id).drop_unique_index(
                instance.key
            )
        except Exception:
            raise DropUniqueIndexError()
        instance.delete()

    @swagger_auto_schema(
        operation_summary="字段列表",
        tags=WorkSheetFieldViewTags,
        query_serializer=worksheetfiled.WorkSheetFieldListSerializer(),
    )
    def list(self, request, *args, **kwargs):
        worksheet_id = self.request.query_params.get("worksheet_id")
        if worksheet_id is not None:
            self.serializer_class = worksheetfiled.WorkSheetFieldListSerializer
            worksheet_id = self.validated_data["worksheet_id"]
            self.queryset = self.queryset.filter(worksheet_id=worksheet_id)
            self.queryset = WorkSheetFieldBatchModelHandler(
                worksheet_id
            ).get_order_queryset()
            self.serializer_class = WorkSheetFieldSerializer
            return super().list(request, *args, **kwargs)
        return Response()

    @swagger_auto_schema(
        operation_summary="字段详情",
        tags=WorkSheetFieldViewTags,
        responses={status.HTTP_200_OK: WorkSheetFieldSerializer()},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="批量保存字段",
        tags=WorkSheetFieldViewTags,
    )
    @action(
        methods=["post"], detail=False, serializer_class=BatchWorkSheetFieldSerializer
    )
    def batch_save(self, request, *args, **kwargs):
        worksheet_id = self.validated_data["worksheet_id"]
        context = self.get_serializer_context()
        queryset = WorkSheetFieldBatchModelHandler(worksheet_id).batch_save(
            self.validated_data["fields"], context=context
        )
        serializer = WorkSheetFieldSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="获取内置计算方法",
    )
    @action(detail=False, methods=["get"])
    def get_built_in_formula(self, request):
        return Response(dict(FORMULA_BUILTIN))
