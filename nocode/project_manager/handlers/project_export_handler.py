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
from itsm.project.handler.project_handler import PageModelHandler
from itsm.project.models import Project, ProjectConfig
from itsm.service.models import Service
from nocode.page.models import Page, PageComponent
from nocode.worksheet.models import WorkSheet, WorkSheetField


class ProjectExportHandler:
    def __init__(self, project_key):
        self.project_key = project_key
        self.project = Project.objects.get(key=project_key)

    def _build_project_tag_data(self):
        return self.project.tag_data()

    def _build_project_config_tag_data(self):
        project_config = ProjectConfig.objects.get(project_key=self.project_key)
        return project_config.tag_data()

    def _build_worksheet_tag_data(self):
        worksheets = WorkSheet.objects.filter(project_key=self.project_key)
        data = []
        for worksheet in worksheets:
            data.append(worksheet.tag_data())

        return data

    def _build_worksheet_field_tag_data(self):
        worksheet_ids = WorkSheet.objects.filter(
            project_key=self.project_key
        ).values_list("id", flat=True)
        worksheet_fields = WorkSheetField.objects.filter(worksheet_id__in=worksheet_ids)
        data = {}
        for worksheet_field in worksheet_fields:
            tag_data = worksheet_field.tag_data()
            worksheet_id = tag_data["worksheet_id"]
            data.setdefault(worksheet_id, []).append(tag_data)

        return data

    def _build_page_tag_data(self):
        data = PageModelHandler().tree_data(project_key=self.project_key)

        return data

    def _build_page_component_tag_data(self):
        page_ids = Page.objects.filter(project_key=self.project_key).values_list(
            "id", flat=True
        )

        page_components = PageComponent.objects.filter(page_id__in=page_ids)
        data = {}
        for page_component in page_components:
            tag_data = page_component.tag_data()
            page_id = tag_data["page_id"]
            data[page_id] = tag_data

        return data

    def _build_service_tag_data(self):
        services = Service.objects.filter(project_key=self.project_key)
        data = []
        for service in services:
            data.append(service.tag_data())

        return data

    def build_tag_data(self):
        return {
            "project": self._build_project_tag_data(),
            "project_config": self._build_project_config_tag_data(),
            "worksheet": self._build_worksheet_tag_data(),
            "worksheet_field": self._build_worksheet_field_tag_data(),
            "page": self._build_page_tag_data(),
            "page_component": self._build_page_component_tag_data(),
            "service": self._build_service_tag_data(),
        }
