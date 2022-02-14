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
from blueapps.core.celery.celery import app


from django.test import TestCase, override_settings
from itsm.project.models import Project, ProjectConfig
from nocode.page.handlers.page_handler import PageModelHandler
from nocode.page.views.view import PageComponentViewSet
from nocode.test.page.params import SON_POINT, CREATE_PROJECT_DATA
from nocode.page.models import Page, PageComponent


class TestPageComponent(TestCase):
    def setUp(self) -> None:
        app.conf.update(CELERY_ALWAYS_EAGER=True)
        Project.objects.create(**CREATE_PROJECT_DATA)
        project_config = {"workflow_prefix": "test", "project_key": "test"}
        ProjectConfig.objects.create(**project_config)
        PageModelHandler().create_root(project_key=CREATE_PROJECT_DATA["key"])

    def project_publish(self):
        publish_rep = self.client.post(
            path="/api/project/manager/publish/",
            data=json.dumps({"project_key": "test"}),
            content_type="application/json",
        )
        self.assertEqual(publish_rep.data["code"], "OK")
        self.assertEqual(publish_rep.data["message"], "success")

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_batch_save(self) -> None:
        root = Page.objects.get(key="root", project_key=CREATE_PROJECT_DATA["key"])
        for point in SON_POINT:
            point.setdefault("parent_id", root.id)
            resp = self.client.post("/api/page_design/page/", point)
            self.assertEqual(resp.data["result"], True)

        page = Page.objects.get(name="page1", type="FUNCTION")
        data = {
            "page_id": page.id,
            "components": [
                {
                    "page_id": page.id,
                    "type": "FUNCTION",
                    "value": 29,
                    "config": {"name": "test", "desc": "test"},
                }
            ],
        }

        res = self.client.post(
            "/api/page_design/page_component/batch_save/",
            data,
            content_type="application/json",
        )
        self.assertEqual(res.data["result"], True)
        self.assertEqual(res.data["message"], "success")
        self.assertEqual(len(res.data["data"]), 1)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_get_components_action(self):
        self.test_batch_save()
        project_key = CREATE_PROJECT_DATA["key"]
        url = f"/api/page_design/page_component/get_components_action/?project_key={project_key}"
        res = self.client.get(url)
        self.assertEqual(res.data["result"], True)
        self.assertEqual(res.data["data"][0]["actions"][0]["name"], "test")

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_generate_open_link(self):
        self.test_batch_save()

        page = Page.objects.get(name="page3", type="SHEET")
        component_data = {
            "page_id": page.id,
            "components": [
                {
                    "page_id": page.id,
                    "type": "SHEET",
                    "value": 29,
                    "config": {"name": "test", "desc": "test"},
                }
            ],
        }

        res = self.client.post(
            "/api/page_design/page_component/batch_save/",
            component_data,
            content_type="application/json",
        )
        self.assertEqual(res.data["result"], True)
        self.assertEqual(res.data["message"], "success")

        link_data = {
            "page_id": page.id,
            "service_id": 29,
            "project_key": "test",
            "end_time": "2099-12-31 23:59:59",
        }

        res = self.client.post(
            "/api/page_design/page_component/generate_open_link/",
            link_data,
            content_type="application/json",
        )
        self.assertEqual(res.data["result"], True)
        self.assertEqual(res.data["message"], "success")
        self.assertEqual(len(res.data["data"]), 1)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_clear_open_link(self):
        self.test_generate_open_link()
        page = Page.objects.get(name="page3", type="SHEET")

        clear_data = {"page_id": page.id, "project_key": "test"}
        res = self.client.post(
            path="/api/project/manager/publish/",
            data=clear_data,
            content_type="application/json",
        )
        self.assertEqual(res.data["code"], "OK")
        self.assertEqual(res.data["message"], "success")

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_add_components_collection(self):
        self.test_batch_save()
        publish_rep = self.client.post(
            path="/api/project/manager/publish/",
            data=json.dumps({"project_key": "test"}),
            content_type="application/json",
        )
        self.assertEqual(publish_rep.data["code"], "OK")
        self.assertEqual(publish_rep.data["message"], "success")

        page = Page.objects.get(name="page1", type="FUNCTION")
        component = PageComponent.objects.get(type="FUNCTION", page_id=page.id)

        res = self.client.post(
            "/api/page_design/collection/",
            data={"component_id": component.id},
            content_type="application/json",
        )
        self.assertEqual(res.data["code"], "OK")
        self.assertEqual(res.data["message"], "success")

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_cancel_components_collection(self):
        self.test_batch_save()
        publish_rep = self.client.post(
            path="/api/project/manager/publish/",
            data=json.dumps({"project_key": "test"}),
            content_type="application/json",
        )
        self.assertEqual(publish_rep.data["code"], "OK")
        self.assertEqual(publish_rep.data["message"], "success")

        page = Page.objects.get(name="page1", type="FUNCTION")
        component = PageComponent.objects.get(type="FUNCTION", page_id=page.id)

        res = self.client.post(
            "/api/page_design/collection/",
            data={"component_id": component.id},
            content_type="application/json",
        )
        self.assertEqual(res.data["code"], "OK")
        self.assertEqual(res.data["message"], "success")

        url = f"/api/page_design/collection/cancel_collection/?component_id={component.id}"
        res = self.client.delete(url)
        self.assertEqual(res.data["code"], "OK")
        self.assertEqual(res.data["message"], "success")

    def test_get_user_collection(self):
        self.test_add_components_collection()
        url = "/api/page_design/collection/get_user_collection/"
        res = self.client.get(url)
        self.assertEqual(res.data["code"], "OK")
        self.assertEqual(res.data["message"], "success")
        self.assertEqual(len(res.data["data"]), 1)

    actions_exempt = [
        "create",
        "destroy",
        "list",
        "update",
        "partial_update",
        "retrieve",
    ]
    swagger_test_view = PageComponentViewSet
