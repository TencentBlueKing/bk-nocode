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
from itsm.project.models import Project
from nocode.project_manager.models import ProjectVersion


class ProjectHandler:
    def __init__(self, project_key=None):
        self.project_key = project_key

    @property
    def instance(self):
        try:
            instance = Project.objects.get(key=self.project_key)
        except Project.DoesNotExist:
            instance = None
        return instance

    def user_group_change_project_change(self):
        project = self.instance
        project.publish_status = "CHANGED"
        project.save()

    def exist(self):
        try:
            Project.objects.get(key=self.project_key)
        except Project.DoesNotExist:
            return False
        return True


class ProjectVersionHandler:
    def __init__(self, project_key):
        self.project = Project.objects.get(key=project_key)
        self.version = ProjectVersion.objects.get(
            project_key=project_key, version_number=self.project.version_number
        )

    def get_page_data(self):
        return self.version.page

    def get_page_component(self, page_id):
        return self.version.page_component.get(page_id, [])
