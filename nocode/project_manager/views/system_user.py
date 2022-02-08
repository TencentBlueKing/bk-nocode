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

from blueapps.account.models import User
from nocode.page.handlers.moudle_handler import ModelViewSet
from nocode.project_manager.permission import SystemUserPermission
from nocode.project_manager.serializers.system_user import (
    SystemUserModelSerializer,
    SystemUserOperateSerializer,
)


class SuperUserViewSet(ModelViewSet):
    queryset = User.objects.filter(is_superuser=True, is_active=True)
    serializer_class = SystemUserModelSerializer
    permission_classes = (SystemUserPermission,)

    filter_fields = {
        "username": ["exact", "contains", "icontains"],
    }

    def remove_superuser(self, user):
        user.is_superuser = False
        user.is_active = True
        user.save()
        return user

    def superuser_operate(self, username, operate):
        user_obj = User.objects.filter(username=username).first()
        if operate == "ADD":
            if not user_obj:
                return User.objects.create(
                    username=username, is_superuser=True, is_active=True
                )

            user_obj.is_superuser = True
            user_obj.is_active = True
            user_obj.save()
            return user_obj

        if operate == "DELETE":
            if not user_obj:
                return None
            return self.remove_superuser(user_obj)

    @swagger_auto_schema(
        operation_summary="超级管理员操作",
    )
    @action(
        detail=False, methods=["post"], serializer_class=SystemUserOperateSerializer
    )
    def operate_superuser(self, request, *args, **kwargs):
        serializer = SystemUserOperateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        operate_action = validated_data["action"]
        username_list = validated_data["users"]
        date_struct = []
        for username in username_list:
            user = self.superuser_operate(
                username=username, operate=operate_action.upper()
            )
            if not user:
                continue
            date_struct.append(
                {
                    "id": user.id,
                    "username": user.username,
                    "is_superuser": user.is_superuser,
                    "is_active": user.is_active,
                }
            )
        return Response(data=date_struct)
