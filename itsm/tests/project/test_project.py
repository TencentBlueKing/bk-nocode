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
import json

import mock
from django.test import TestCase, override_settings

from itsm.project.handler.permit_engine_handler import PermitInitManagerDispatcher
from itsm.project.models import ServiceCatalog, ProjectSettings, Project, ProjectConfig
from itsm.tests.project.params import CREATE_PROJECT_DATA


class TestProject(TestCase):
    def setUp(self) -> None:
        ProjectSettings.objects.all().delete()
        ProjectConfig.objects.all().delete()
        Project.objects.all().delete()
        ServiceCatalog.objects.all().delete()

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch.object(PermitInitManagerDispatcher, "init_permit")
    def test_create_project(self, mock_result):
        mock_result.return_value = 1
        resp = self.client.post(
            "/api/project/projects/",
            {},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["result"], False)
        self.assertEqual(resp.data["code"], "VALIDATE_ERROR")

        resp = self.client.post(
            "/api/project/projects/",
            json.dumps(CREATE_PROJECT_DATA),
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data["result"], True)

        service_catalog = len(
            ServiceCatalog.objects.filter(project_key=CREATE_PROJECT_DATA["key"])
        )

        self.assertEqual(service_catalog, 7)

        self.assertEqual(
            ProjectConfig.objects.filter(
                project_key=CREATE_PROJECT_DATA["key"]
            ).exists(),
            True,
        )

    def tearDown(self) -> None:
        ProjectSettings.objects.all().delete()
        Project.objects.all().delete()
        ServiceCatalog.objects.all().delete()

    # @override_settings(MIDDLEWARE=('itsm.tests.middlewares.OverrideMiddleware',))
    # def test_update_records(self) -> None:
    #     resp = self.client.post("/api/project/projects/", CREATE_PROJECT_DATA)
    #
    #     project_key = resp.data["data"]["key"]
    #
    #     url = "/api/project/projects/{}/update_project_record/".format(project_key)
    #     update_project_record_resp = self.client.post(url)
    #
    #     self.assertEqual(update_project_record_resp.data["result"], True)
    #     self.assertEqual(update_project_record_resp.data["code"], "OK")
    #
    #     self.assertEqual(UserProjectAccessRecord.objects.filter(project_key=project_key).exists(), True)
