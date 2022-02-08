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

from nocode.project_manager.exceptions import (
    ProjectDoesNotExists,
    ProjectVersionDoesNotExists,
)
from nocode.project_manager.handlers.module_handler import ProjectModuleHandler
from nocode.project_manager.models import ProjectVersion


class ProjectPublishSerializer(serializers.Serializer):
    project_key = serializers.CharField(help_text=_("项目key"))

    def validate_project_key(self, project_key):
        try:
            ProjectModuleHandler(project_key).handler.instance
        except Exception:
            raise ProjectDoesNotExists()

        return project_key


class ProjectVersionQuerySerializer(serializers.Serializer):
    project_key = serializers.CharField(help_text=_("项目key"))
    version_number = serializers.CharField(help_text=_("项目版本ID"))

    def validate_project_key(self, project_key):
        try:
            ProjectModuleHandler(project_key).handler.instance
        except Exception:
            raise ProjectDoesNotExists()

        return project_key

    def validate(self, attrs):
        version_number = attrs.get("version_number")
        project_key = attrs.get("project_key")

        if not ProjectVersion.objects.filter(
            project_key=project_key, version_number=version_number
        ).exists():
            raise ProjectVersionDoesNotExists()

        return attrs


class ProjectPublishLogSerializer(serializers.Serializer):
    task_id = serializers.IntegerField(help_text=_("任务ID"))


class PageComponentQuerySerializer(ProjectVersionQuerySerializer):
    page_id = serializers.CharField(help_text=_("页面id"))


class WorkSheetFieldQuerySerializer(ProjectVersionQuerySerializer):
    worksheet_id = serializers.CharField(help_text=_("工作表ID"))


class OpenLinkQuerySerializer(serializers.Serializer):
    token = serializers.CharField(help_text=_("页面访问token"))
