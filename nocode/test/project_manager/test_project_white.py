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
import mock
from django.test import TestCase, override_settings

from blueapps.core.celery.celery import app
from itsm.component.constants import OPERATE_CATALOG
from itsm.project.handler.project_handler import ProjectHandler
from itsm.project.models import Project
from nocode.project_manager.models import ProjectWhite
from nocode.test.page.params import CREATE_PROJECT_DATA
from nocode.test.worksheet.params import WORKSHEET_DATA
from nocode.worksheet.handlers.moudule_handler import ServiceHandler, DjangoHandler


class TestProjectWhiteView(TestCase):
    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def setUp(self) -> None:
        app.conf.update(CELERY_ALWAYS_EAGER=True)
        project = Project.objects.create(**CREATE_PROJECT_DATA)
        ProjectHandler(instance=project).init_operate_catalogs(OPERATE_CATALOG)
        self.worksheet_id = None

    def create_worksheet(self):
        url = "/api/worksheet/sheets/"
        res = self.client.post(
            url, data=WORKSHEET_DATA, content_type="application/json"
        )
        self.assertEqual(res.data["data"]["name"], WORKSHEET_DATA["name"])
        return res.data["data"]["id"]

    def fields_batch_save(self, worksheet_id):
        url = "/api/worksheet/fields/batch_save/"

        worksheet_field = {
            "worksheet_id": worksheet_id,
            "fields": [
                {
                    "meta": {},
                    "api_info": {},
                    "choice": [],
                    "kv_relation": {},
                    "key": "shu_zi_1",
                    "name": "数字1",
                    "desc": "",
                    "type": "INT",
                    "layout": "COL_12",
                    "validate_type": "OPTION",
                    "source_type": "CUSTOM",
                    "api_instance_id": 0,
                    "default": "0",
                    "worksheet_id": worksheet_id,
                    "regex": "EMPTY",
                },
                {
                    "meta": {},
                    "api_info": {},
                    "choice": [],
                    "kv_relation": {},
                    "create_at": "2022-01-27 15:37:28",
                    "key": "shu_zi_2",
                    "name": "数字2",
                    "desc": "",
                    "type": "INT",
                    "layout": "COL_12",
                    "validate_type": "OPTION",
                    "source_type": "CUSTOM",
                    "api_instance_id": 0,
                    "default": "0",
                    "worksheet_id": worksheet_id,
                    "regex": "EMPTY",
                },
            ],
        }

        res = self.client.post(
            url, data=worksheet_field, content_type="application/json"
        )
        self.assertEqual(len(res.data["data"]), 2)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch.object(ServiceHandler, "init_service")
    @mock.patch.object(DjangoHandler, "init_db")
    @mock.patch.object(ServiceHandler, "migrate_service")
    def test_create_project_white(self, mock_result, mock_back, mock_callback):
        mock_result.return_value = {}
        mock_back.return_value = {}
        mock_callback.return_value = {}
        worksheet_id = self.create_worksheet()
        self.worksheet_id = worksheet_id
        self.fields_batch_save(worksheet_id)
        add_data = {
            "project_key": "test",
            "value": worksheet_id,
            "projects": ["0", "public"],
            "type": "WORKSHEET",
        }
        url = "/api/project/project_white/"
        res = self.client.post(url, data=add_data, content_type="application/json")
        self.assertEqual(res.data["result"], True)
        self.assertEqual(res.data["message"], "success")
        self.assertEqual(res.data["data"]["granted_project"], add_data["projects"])

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch.object(ServiceHandler, "init_service")
    @mock.patch.object(DjangoHandler, "init_db")
    @mock.patch.object(ServiceHandler, "migrate_service")
    def test_list_project_white(self, mock_result, mock_back, mock_callback):
        mock_result.return_value = {}
        mock_back.return_value = {}
        mock_callback.return_value = {}
        self.test_create_project_white()
        url = "/api/project/project_white/"
        res = self.client.get(url)
        self.assertEqual(res.data["result"], True)
        self.assertEqual(res.data["message"], "success")
        self.assertEqual(len(res.data["data"]["items"]), 1)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch.object(ServiceHandler, "init_service")
    @mock.patch.object(DjangoHandler, "init_db")
    @mock.patch.object(ServiceHandler, "migrate_service")
    def test_operate_white_list(self, mock_result, mock_back, mock_callback):
        mock_result.return_value = {}
        mock_back.return_value = {}
        mock_callback.return_value = {}
        self.test_create_project_white()

        project_white = ProjectWhite.objects.get(
            project_key="test", value=self.worksheet_id
        )
        url = f"/api/project/project_white/{project_white.id}/operate_white_list/"
        data = {"id": project_white.id, "projects": ["PMM", "ROOM"]}
        res = self.client.post(url, data=data, content_type="application/json")
        self.assertEqual(res.data["result"], True)
        self.assertEqual(res.data["message"], "success")

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch.object(ServiceHandler, "init_service")
    @mock.patch.object(DjangoHandler, "init_db")
    @mock.patch.object(ServiceHandler, "migrate_service")
    def test_get_project_granted_by(self, mock_result, mock_back, mock_callback):
        mock_result.return_value = {}
        mock_back.return_value = {}
        mock_callback.return_value = {}
        self.test_create_project_white()

        url = "/api/project/project_white/get_project_granted_by/?project_key={}"

        res = self.client.get(url.format("0"))
        self.assertEqual(res.data["result"], True)
        self.assertEqual(res.data["message"], "success")
        self.assertEqual(len(res.data["data"]), 1)

        res = self.client.get(url.format("public"))
        self.assertEqual(res.data["result"], True)
        self.assertEqual(res.data["message"], "success")

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch.object(ServiceHandler, "init_service")
    @mock.patch.object(DjangoHandler, "init_db")
    @mock.patch.object(ServiceHandler, "migrate_service")
    def test_get_worksheets(self, mock_result, mock_back, mock_callback):
        mock_result.return_value = {}
        mock_back.return_value = {}
        mock_callback.return_value = {}
        self.test_create_project_white()

        url = "/api/project/project_white/get_worksheets/?project=0&relate_project=test"
        res = self.client.get(url)
        self.assertEqual(res.data["result"], True)
        self.assertEqual(res.data["message"], "success")
        self.assertEqual(len(res.data["data"]), 1)
