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
from rest_framework import serializers

from itsm.project.handler.utils import change_so_project_change
from nocode.permit.handlers.moudle_handler import ProjectHandler
from nocode.permit.models import UserGroup


class UserGroupModelSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False, max_length=32, min_length=5)
    project_key = serializers.CharField(required=True, max_length=32)

    def validate(self, attrs):
        name = attrs.get("name")
        project_key = attrs.get("project_key")

        if not ProjectHandler(project_key).exist():
            raise serializers.ValidationError(
                "用户组创建失败，project={}对应的项目不存在".format(project_key)
            )

        if UserGroup.objects.filter(name=name, project_key=project_key).exists():
            raise serializers.ValidationError("用户组创建失败，项目下已经存在名为{}的用户组".format(name))

        return attrs

    def create(self, validated_data):
        change_so_project_change(validated_data["project_key"])
        return super(UserGroupModelSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        change_so_project_change(instance.project_key)
        return super(UserGroupModelSerializer, self).update(instance, validated_data)

    class Meta:
        model = UserGroup
        fields = "__all__"
        # 只读字段在创建和更新时均被忽略
        read_only_fields = ("creator", "create_at", "update_at", "updated_by")
