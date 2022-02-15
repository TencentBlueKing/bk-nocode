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
from django.test import override_settings
from blueapps.core.celery.celery import app

from itsm.component.constants import OPERATE_CATALOG
from itsm.project.handler.project_handler import ProjectHandler
from itsm.project.models import Project
from nocode.base.base_tests import MyTestCase
from nocode.test.page.params import CREATE_PROJECT_DATA

from nocode.test.worksheet.params import WORKSHEET_DATA
from nocode.worksheet.handlers.moudule_handler import ServiceHandler, DjangoHandler
from nocode.worksheet.views.worksheetfield import WorkSheetFieldViewSet


class TestWorkSheetFieldsView(MyTestCase):
    def setUp(self) -> None:
        app.conf.update(CELERY_ALWAYS_EAGER=True)
        project = Project.objects.create(**CREATE_PROJECT_DATA)
        ProjectHandler(instance=project).init_operate_catalogs(OPERATE_CATALOG)

    def create_worksheet(self):
        url = "/api/worksheet/sheets/"
        res = self.client.post(
            url, data=WORKSHEET_DATA, content_type="application/json"
        )
        self.assertEqual(res["name"], WORKSHEET_DATA["name"])
        return res["id"]

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch.object(ServiceHandler, "init_service")
    @mock.patch.object(DjangoHandler, "init_db")
    def test_batch_save(self, mock_result, mock_back):
        worksheet_id = self.create_worksheet()
        mock_result.return_value = {}
        mock_back.return_value = {}
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
        self.assertEqual(len(res), 2)

    swagger_test_view = WorkSheetFieldViewSet

    actions_exempt = [
        "create",
        "destroy",
        "retrieve",
        "list",
        "update",
        "partial_update",
        "get_built_in_formula",
        "batch_save",
        "download_file",
    ]
