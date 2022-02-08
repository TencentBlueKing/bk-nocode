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
import datetime

from nocode.project_manager.models import OperateLog


class OperateLogHandler:
    log_model = OperateLog.objects

    @classmethod
    def log_create(cls, *args, **kwargs):
        project_key = kwargs.get("project_key")
        module = kwargs.get("module")
        content = kwargs.get("content")
        operator = kwargs.get("operator")

        OperateLog.objects.create(
            project_key=project_key, module=module, content=content, operator=operator
        )

    def filter_project_name(self, queryset, project_name):
        from itsm.project.handler.project_handler import ProjectHandler

        project_keys = (
            ProjectHandler()
            .all_project.filter(name__icontains=project_name)
            .values_list("key", flat=True)
        )
        queryset = queryset.filter(project_key__in=project_keys)
        return queryset

    def filter_time(self, start_time, end_time, queryset):
        end_time = datetime.datetime.strptime(
            end_time, "%Y-%m-%d"
        ).date() + datetime.timedelta(days=1)
        queryset = queryset.filter(create_at__gte=start_time, create_at__lte=end_time)
        return queryset
