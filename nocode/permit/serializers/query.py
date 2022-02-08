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
from django.utils.translation import ugettext as _

from nocode.permit.handlers.moudle_handler import ProjectHandler


class WorkSheetListSerializer(serializers.Serializer):
    project_key = serializers.CharField(help_text=_("应用唯一标识"))

    def validate_project_key(self, project_key):
        if not ProjectHandler(project_key).exist():
            raise serializers.ValidationError(detail=_("对应的项目不存在！"))
        return project_key

    class Meta:
        swagger_schema_fields = {"example": {"project_key": 0}}


class QueryPagePermitSerializer(WorkSheetListSerializer):
    pass


class QueryActionPermitSerializer(WorkSheetListSerializer):
    page_id = serializers.CharField(help_text="页面ID", max_length=32)
