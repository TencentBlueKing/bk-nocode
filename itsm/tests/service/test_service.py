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

# This file demonstrates writing tests using the unittest module. These will pass
# when you run "manage.py test".
# Replace this with more appropriate tests for your application.

import json
import sys
import datetime

import mock
from django.test import TestCase, override_settings

from itsm.component.constants import OPERATE_CATALOG
from itsm.project.handler.project_handler import ProjectHandler
from itsm.project.models import Project
from itsm.tests.service.params import CREATE_SERVICE_DATA, CONFIGS
from itsm.workflow.models import WorkflowVersion
from itsm.service.models import Service
from nocode.worksheet.models import WorkSheet


class ServiceTest(TestCase):
    def json(self, data):
        return json.dumps(data)

    def tearDown(self) -> None:
        Service.objects.filter(name="测试服务").delete()
        Service.objects.filter(name="测试服务2").delete()

    def setUp(self):
        """准备数据"""
        self.service = None
        self.operator = "itsm_admin"
        self.data = {
            "name": "service_create_test_{}".format(
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            ),
            "key": "test",
            "workflow": WorkflowVersion.objects.first(),
            "creator": self.operator,
        }
        self.worksheet_data = {
            "creator": "admin",
            "create_at": "2021-09-18 15:51:22",
            "update_at": "2021-09-18 15:51:22",
            "updated_by": "admin",
            "is_deleted": False,
            "name": "这是一张测试工作表",
            "desc": "test_worksheet",
            "key": "test_worksheet",
            "project_key": "0",
        }
        self.create_project_data = {
            "key": "test",
            "name": "test",
            "logo": "",
            "color": [],
            "creator": "admin",
            "create_at": "2021-05-30 17:16:40",
            "updated_by": "test_admin",
            "update_at": "2021-05-30 17:16:40",
        }
        project = Project.objects.create(**self.create_project_data)
        ProjectHandler(instance=project).init_operate_catalogs(OPERATE_CATALOG)

    def test_create_service_actions_auth(self):
        """
        测试新建服务时候的权限校验
        """
        print(sys._getframe().f_code.co_name)
        self.service = Service.objects.create(**self.data)
        # resource_info = [
        #     {
        #         "resource_id": str(self.service.id),
        #         "resource_name": self.service.name,
        #         "resource_type": self.service.auth_resource["resource_type"],
        #     }
        # ]

    @staticmethod
    def auth_result(apply_actions, resource_info):
        iam_client = mock.MagicMock()
        actions_result = {action: True for action in apply_actions}
        iam_client.resource_multi_actions_allowed.return_value = {
            str(resource["resource_id"]): actions_result for resource in resource_info
        }
        auth_actions = iam_client.resource_multi_actions_allowed(
            apply_actions, [resource_info]
        )
        denied_actions = []
        for action, result in auth_actions.items():
            if action in apply_actions and result is False:
                denied_actions.append(action)
        return len(denied_actions) == 0

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.ticket.serializers.ticket.get_bk_users")
    @mock.patch("itsm.component.utils.misc.get_bk_users")
    def test_create_service(self, patch_misc_get_bk_users, path_get_bk_users):
        patch_misc_get_bk_users.return_value = {}
        path_get_bk_users.return_value = {}

        url = "/api/service/projects/"
        worksheet_id = WorkSheet.objects.create(**self.worksheet_data).id

        CREATE_SERVICE_DATA.setdefault("worksheet_ids", [worksheet_id])
        resp = self.client.post(
            url, json.dumps(CREATE_SERVICE_DATA), content_type="application/json"
        )
        self.assertEqual(resp.data["result"], True)
        self.assertEqual(resp.data["code"], "OK")

    # @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    # @mock.patch("itsm.ticket.serializers.ticket.get_bk_users")
    # @mock.patch("itsm.component.utils.misc.get_bk_users")
    # def test_import(self, patch_misc_get_bk_users, path_get_bk_users):
    #     patch_misc_get_bk_users.return_value = {}
    #     path_get_bk_users.return_value = {}
    #     url = "/api/service/projects/"
    #     resp = self.client.post(url, CREATE_SERVICE_DATA)
    #
    #     service_id = resp.data["data"]["id"]
    #
    #     import_from_template_url = (
    #         "/api/service/projects/" "{}/import_from_template/".format(service_id)
    #     )
    #
    #     resp = self.client.post(import_from_template_url, {"table_id": 8})
    #
    #     self.assertEqual(resp.data["result"], True)
    #     self.assertEqual(resp.data["code"], "OK")
    #
    #     workflow = Workflow.objects.get(
    #         id=Service.objects.get(id=service_id).workflow.workflow_id
    #     )
    #     version = workflow.create_version()
    #
    #     # 判断字段是否成功导入
    #     fields = version.get_first_state_fields()
    #     self.assertEqual(fields[0]["name"], "标题")
    #     self.assertEqual(fields[1]["name"], "申请类型")
    #     self.assertEqual(fields[2]["name"], "组织")
    #     self.assertEqual(fields[3]["name"], "申请内容")
    #     self.assertEqual(fields[4]["name"], "申请理由")
    #
    #     service = Service.objects.get(id=service_id)
    #     service.workflow = version
    #     service.save()
    #
    #     # 测试从服务导入
    #     data = {
    #         "name": "测试服务2",
    #         "desc": "测试服务",
    #         "key": "request",
    #         "catalog_id": 2,
    #         "project_key": "0",
    #     }
    #     resp = self.client.post(url, data)
    #     service_id = resp.data["data"]["id"]
    #
    #     import_from_service_url = (
    #         "/api/service/projects/" "{}/import_from_service/".format(service_id)
    #     )
    #
    #     resp = self.client.post(import_from_service_url, {"service_id": service.id})
    #
    #     self.assertEqual(resp.data["result"], True)
    #     self.assertEqual(resp.data["code"], "OK")
    #
    #     workflow = Workflow.objects.get(
    #         id=Service.objects.get(id=service_id).workflow.workflow_id
    #     )
    #     version = workflow.create_version()
    #
    #     # 判断字段是否成功导入
    #     fields = version.get_first_state_fields()
    #     self.assertEqual(fields[0]["name"], "标题")
    #     self.assertEqual(fields[1]["name"], "申请类型")
    #     self.assertEqual(fields[2]["name"], "组织")
    #     self.assertEqual(fields[3]["name"], "申请内容")
    #     self.assertEqual(fields[4]["name"], "申请理由")

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.ticket.serializers.ticket.get_bk_users")
    @mock.patch("itsm.component.utils.misc.get_bk_users")
    def test_save_configs(self, patch_misc_get_bk_users, path_get_bk_users):
        patch_misc_get_bk_users.return_value = {}
        path_get_bk_users.return_value = {}
        worksheet_id = WorkSheet.objects.create(**self.worksheet_data).id

        CREATE_SERVICE_DATA.setdefault("worksheet_ids", [worksheet_id])
        url = "/api/service/projects/"
        resp = self.client.post(
            url, json.dumps(CREATE_SERVICE_DATA), content_type="application/json"
        )
        self.assertEqual(resp.data["result"], True)
        self.assertEqual(resp.data["code"], "OK")

        service_id = resp.data["data"]["id"]
        save_configs_url = "{}{}/save_configs/".format(url, service_id)

        resp = self.client.post(
            save_configs_url, json.dumps(CONFIGS), content_type="application/json"
        )

        self.assertEqual(resp.data["result"], True)
        self.assertEqual(resp.data["code"], "OK")
