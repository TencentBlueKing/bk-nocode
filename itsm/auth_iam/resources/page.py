# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.

Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.

BK-ITSM 蓝鲸流程服务 is licensed under the MIT License.

License for BK-ITSM 蓝鲸流程服务:
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

# from iam import PathEqDjangoQuerySetConverter


from itsm.auth_iam.resources import ItsmResourceProvider
from nocode.page.models import Page
from nocode.project_manager.models import ProjectVersion
from .basic import ItsmResourceListResult as ListResult
from ...project.models import Project


class PageResourceProvider(ItsmResourceProvider):
    def parse_tree(self, node, data):
        if node["type"] not in ["ROOT", "", "GROUP"]:
            data.append({"id": node["id"], "name": node["name"]})
        for item in node["children"]:
            self.parse_tree(item, data)

    def get_data(self, page_data):
        data = []
        self.parse_tree(page_data, data)
        return data

    def list_instance(self, filter, page, **options):
        """
        flow 上层资源为 project
        """

        if not (filter.parent or filter.search or filter.resource_type_chain):
            return ListResult(results=[], count=0)

        if not filter.parent:
            return ListResult(results=[], count=0)

        project_key = filter.parent["id"]

        project = Project.objects.get(key=project_key)

        page_data = ProjectVersion.objects.get(
            version_number=project.version_number
        ).page

        data = self.get_data(page_data[0])
        count = len(data)

        results = []
        # return
        for item in data[page.slice_from : page.slice_to]:
            results.append({"id": item["id"], "display_name": item["name"]})
        return ListResult(results=results, count=count)

    def fetch_instance_info(self, filter, **options):
        """
        flow 没有定义属性，只处理 filter 中的 ids 字段
        """
        ids = []
        if filter.ids:
            ids = [int(i) for i in filter.ids]
        if not ids:
            return ListResult(results=[])

        page_id = ids[0]
        page = Page._objects.filter(id=page_id).first()
        if page is None:
            return ListResult(results=[])

        project_key = page.project_key
        project = Project.objects.get(key=project_key)
        page_data = ProjectVersion.objects.get(
            version_number=project.version_number
        ).page
        data = self.get_data(page_data[0])
        results = []
        for item in data:
            if item["id"] in ids:
                results.append({"id": str(item["id"]), "display_name": item["name"]})

        return ListResult(results=results)
