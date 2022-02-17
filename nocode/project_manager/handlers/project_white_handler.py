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

from itsm.component.exceptions import ProjectWhiteNotFound
from itsm.project.models import Project
from nocode.base.constants import WORKSHEET
from nocode.project_manager.models import ProjectWhite
from nocode.worksheet.models import WorkSheet, WorkSheetField


class ProjectWhiteHandler:
    def __init__(self, value=None, value_type=None, instance=None):
        self.value = value
        self.type = value_type
        self.obj = instance

    def _get_instance(self):
        instance = self.obj
        if not instance:
            try:
                instance = ProjectWhite.objects.get(value=self.value, type=self.type)
            except ProjectWhite.DoesNotExist:
                raise ProjectWhiteNotFound()
        return instance

    @property
    def instance(self):
        return self._get_instance()

    @property
    def all(self):
        return ProjectWhite.objects.all()

    @classmethod
    def init_white_project(cls, data):
        return ProjectWhite.objects.create(**data)

    def operate_white_project(self, project_list):
        instance = self.instance
        instance.granted_project = {"projects": project_list}
        instance.save()

    def get_projects(self, project_key_list):
        return Project.objects.filter(key__in=project_key_list)

    def get_worksheets(self, project, target_project):
        worksheet_ids = self.all.filter(
            project_key=target_project,
            granted_project__projects__icontains=project,
            type=WORKSHEET,
        ).values_list("value")
        # 授权应用下的表单
        worksheets = WorkSheet.objects.filter(id__in=worksheet_ids).values(
            "id", "name", "key", "fields"
        )
        worksheets_info = []
        for item in worksheets:
            fields = WorkSheetField.objects.filter(id__in=item["fields"]).values(
                "id", "key", "name", "type"
            )
            fields_list = []
            for field in fields:
                fields_list.append(field)
            item["fields"] = fields_list
            worksheets_info.append(item)
        return worksheets_info

    def get_project_granted_by(self, project_key):
        project_key_list = self.all.filter(
            granted_project__projects__icontains=project_key, type="WORKSHEET"
        ).values_list("project_key", flat=True)
        project_queryset = self.get_projects(project_key_list).values("key", "name")
        return [item for item in project_queryset]

    def is_project_in_white_list(self, source_project_key):
        white_list = self.instance.granted_project["projects"]
        if source_project_key in white_list:
            return True
