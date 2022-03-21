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

from itsm.service.models import Service
from nocode.data_engine.exceptions import PageComponentError
from nocode.project_manager.models import ProjectVersion
from nocode.worksheet.handlers.worksheet_handler import WorkSheetModelHandler


class PageComponentHandler:
    @classmethod
    def get_project_by_version_number(cls, version_number):
        version = ProjectVersion.objects.get(version_number=version_number)
        return version.project_key

    @classmethod
    def exists(cls, page_id, version_number):
        version = ProjectVersion.objects.get(version_number=version_number)
        if str(page_id) not in version.page_component.keys():
            return False
        return True

    @classmethod
    def get_list_component_config(cls, page_id, version_number):
        version = ProjectVersion.objects.get(version_number=version_number)
        page_components = version.page_component.get(str(page_id))
        if len(page_components) != 1:
            raise PageComponentError()
        return page_components[0]

    @classmethod
    def get_chart_component_config(cls, page_id, page_component_id, version_number):
        version = ProjectVersion.objects.get(version_number=version_number)
        page_components = version.page_component.get(str(page_id))
        for page_component in page_components:
            if page_component.get("id") == page_component_id:
                return [page_component]


class WorkSheetHandler:
    def __init__(self, worksheet_id):
        self.worksheet_id = worksheet_id
        self.handler = WorkSheetModelHandler(worksheet_id)

    def get_instance(self):
        return self.handler.instance

    def get_fields(self):
        return self.handler.fields

    @classmethod
    def exists(cls, worksheet_id, version_number):
        version = ProjectVersion.objects.get(version_number=version_number)
        if str(worksheet_id) not in version.worksheet_field.keys():
            return False
        return True


class ServiceHandler:
    def __init__(self, service_id, worksheet_id):
        self.service_id = service_id
        self.worksheet_id = worksheet_id

    def get_keys(self):
        service = Service._objects.get(id=self.service_id)
        first_state_fields = service.first_state_fields
        keys = []
        upload_keys = []
        for field in first_state_fields:
            if field["meta"].get("worksheet"):
                worksheet_id = field["meta"]["worksheet"]["id"]
                if self.worksheet_id == worksheet_id:
                    keys.append(
                        "contents__{}".format(field["meta"]["worksheet"]["field_key"])
                    )
                    if field["type"] in ["IMAGE", "FILE"]:
                        upload_keys.append(
                            "contents__{}".format(
                                field["meta"]["worksheet"]["field_key"]
                            )
                        )
        return keys, upload_keys
