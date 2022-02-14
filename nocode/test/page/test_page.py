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
from django.test import TestCase, override_settings

from itsm.project.handler.project_handler import PageModelHandler
from itsm.project.models import Project
from nocode.page.views.view import PageModelViewSet
from nocode.test.page.params import CREATE_PROJECT_DATA, SON_POINT
from nocode.page.models import Page, PageComponent


class TestPage(TestCase):
    def setUp(self) -> None:
        Project.objects.all().delete()
        Page.objects.all().delete()
        PageComponent.objects.all().delete()

        Project.objects.get_or_create(**CREATE_PROJECT_DATA)
        PageModelHandler().create_root(project_key=CREATE_PROJECT_DATA["key"])

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_tree_view(self) -> None:
        key = CREATE_PROJECT_DATA["key"]
        root = Page.objects.get(key="root", project_key=key)
        for point in SON_POINT:
            point.setdefault("parent_id", root.id)
            resp = self.client.post("/api/page_design/page/", point)
            self.assertEqual(resp.data["result"], True)
        self.assertEqual(len(Page.objects.filter(project_key=key)), 4)

        resp = self.client.get(f"/api/page_design/page/tree_view/?project_key={key}")
        children = resp.data["data"][0]["children"]
        self.assertEqual(len(children), 3)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_move(self) -> None:
        key = CREATE_PROJECT_DATA["key"]
        self.test_tree_view()

        children = (
            Page.objects.get(project_key=key, key="root")
            .get_children()
            .order_by("order")
        )
        data = {
            "new_order": 0,
            "parent_id": int(children.last().parent_id),
            "project_key": key,
        }
        res = self.client.put(
            f"/api/page_design/page/{children.last().id}/move/",
            data,
            content_type="application/json",
        )
        self.assertEqual(res.data["result"], True)
        new_children = (
            Page.objects.get(project_key=key, key="root")
            .get_children()
            .order_by("order")
        )
        new_sort = new_children.values_list("id", flat=True)
        self.assertEqual(children.first().id, new_sort[0])

    actions_exempt = ["create", "destroy", "list", "update", "partial_update"]
    swagger_test_view = PageModelViewSet
