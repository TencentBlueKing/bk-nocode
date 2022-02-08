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

from itsm.project.handler.utils import change_so_project_change
from nocode.base.base_viewset import BaseModelViewSet
from nocode.permit.models import UserGroup
from nocode.permit.permission import UserGroupPermission
from nocode.permit.serializers import query
from nocode.permit.serializers.user_group import UserGroupModelSerializer

UserGroupTags = ["user_group"]


class UserGroupModelViewSet(BaseModelViewSet):
    queryset = UserGroup.objects.all()
    serializer_class = UserGroupModelSerializer
    permission_classes = (UserGroupPermission,)

    def perform_destroy(self, instance):
        change_so_project_change(instance.project_key)
        super(UserGroupModelViewSet, self).perform_destroy(instance)

    @swagger_auto_schema(
        operation_summary="用户组列表",
        tags=UserGroupTags,
        query_serializer=query.WorkSheetListSerializer(),
    )
    def list(self, request, *args, **kwargs):
        project_key = self.request.query_params.get("project_key")
        if project_key is not None:
            self.serializer_class = query.WorkSheetListSerializer
            project_key = self.validated_data["project_key"]
            self.queryset = self.filter_queryset(
                self.queryset.filter(project_key=project_key)
            )
            self.serializer_class = UserGroupModelSerializer
            return super().list(request, *args, **kwargs)

        return Response()
