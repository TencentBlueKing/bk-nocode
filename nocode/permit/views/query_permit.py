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
from nocode.permit.handlers.permit_handler import PermitHandler
from nocode.permit.serializers import query

Permit_Query_Tags = ["permit_query"]


class PermitQueryViewSet(BaseApiViewSet):
    @swagger_auto_schema(
        operation_summary="查询导航的权限",
        tags=Permit_Query_Tags,
        query_serializer=query.QueryPagePermitSerializer(),
    )
    @action(
        detail=False, methods=["get"], serializer_class=query.QueryPagePermitSerializer
    )
    def get_page_permit(self, request, *args, **kwargs):
        project_key = self.validated_data["project_key"]
        data = PermitHandler(project_key, request).get_page_permit()
        return Response(data)

    @swagger_auto_schema(
        operation_summary="查询某页所有按钮的权限",
        tags=Permit_Query_Tags,
        query_serializer=query.QueryActionPermitSerializer(),
    )
    @action(
        detail=False,
        methods=["get"],
        serializer_class=query.QueryActionPermitSerializer,
    )
    def get_action_permit(self, request, *args, **kwargs):
        project_key = self.validated_data["project_key"]
        page_id = self.validated_data["page_id"]
        data = PermitHandler(project_key, request).get_action_permit(page_id)
        return Response(data)
