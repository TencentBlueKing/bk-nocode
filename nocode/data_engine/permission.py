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
import json

from django.conf import settings
from rest_framework import permissions
from django.utils.translation import ugettext as _

from nocode.base.base_permission import BasePermission
from nocode.base.constants import WORKSHEET
from nocode.data_engine.handlers.module_handlers import PageComponentHandler
from nocode.project_manager.handlers.project_white_handler import (
    ProjectWhiteHandler,
)


class ListDataAccessPermission:
    def get_project_key(self, version_number):
        return PageComponentHandler.get_project_by_version_number(version_number)

    def has_permission(self, request, view):
        if view.action in ["list_component_data"]:
            page_id = request.data.get("page_id")
            project_key = request.data.get("project_key", None)
            if project_key is None:
                version_number = request.data.get("version_number", None)
                project_key = self.get_project_key(version_number)
            return BasePermission(request).have_page_access_resource(
                project_key, page_id
            )
        if view.action == "export_list_component_data":
            page_id = request.data.get("page_id")
            project_key = request.data.get("project_key", None)
            if project_key is None:
                version_number = request.data.get("version_number", None)
                project_key = self.get_project_key(version_number)
            return BasePermission(request).have_page_access_resource(
                project_key, page_id
            )
        return True


class ProjectDataPermission(permissions.BasePermission):
    message = _("您没有查询的权限")

    def has_permission(self, request, view):
        token = request.data["token"]
        data_config = self.token_check(token)
        if data_config:
            return self.in_white(data_config)

    def token_check(self, token):
        data_config = settings.REDIS_INST.get(token)
        if data_config:
            config = data_config.decode()
            return json.loads(config)

    def in_white(self, data_config):
        # 是否本应用
        # 字段所属应用
        source_project = data_config["source"]["project_key"]
        # 数据来源表单以及应用
        worksheet_id = data_config["target"]["worksheet_id"]
        # 同一应用下引用
        if source_project == data_config["target"]["project_key"]:
            return True

        return ProjectWhiteHandler(
            value_type=WORKSHEET, value=worksheet_id
        ).is_project_in_white_list(source_project)
