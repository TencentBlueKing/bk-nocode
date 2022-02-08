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
from itsm.project.handler.project_handler import ProjectHandler
from nocode.page.exceptions import OpenLinkVerifyError
from nocode.page.models import PageOpenRecord
from nocode.project_manager.handlers.module_handler import (
    ProjectVersionHandler,
    ServiceModuleHandler,
)


class OpenLinkVerifyHandler:
    def __init__(self, token):
        self.token = token.strip("/")
        try:
            self.page_record = PageOpenRecord.objects.get(token=self.token)
        except PageOpenRecord.DoesNotExist:
            raise OpenLinkVerifyError("该token对应的配置不存在或者已失效")

    def check_service(self, page_component):
        for item in page_component:
            if item["type"] == "SHEET" and item["value"] == str(
                self.page_record.service_id
            ):
                return True

        return False

    def verify(self):
        project_key = self.page_record.project_key
        instance = ProjectHandler(project_key=project_key).instance
        if len(instance.version_number) == 0:
            raise OpenLinkVerifyError("当前应用未发布")
        version = ProjectVersionHandler(
            project_key=project_key, version_number=instance.version_number
        )
        page_components = version.get_version_page_components()
        if str(self.page_record.page_id) not in page_components:
            raise OpenLinkVerifyError("当前页面未发布或已过期")

        page_component = page_components.get(str(self.page_record.page_id))
        if len(page_component) <= 0:
            raise OpenLinkVerifyError("当前页面未发布或已过期")

        if not self.check_service(page_component):
            raise OpenLinkVerifyError("当前页面绑定的功能已经发生变化")

        # 校验service_id 是否存在
        return ServiceModuleHandler.verify(self.page_record.service_id)

    def get_service(self):
        flag = self.verify()
        if not flag:
            raise OpenLinkVerifyError("当前页面绑定的功能不存在")
        return self.page_record.service_id
