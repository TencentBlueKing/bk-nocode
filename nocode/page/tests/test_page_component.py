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
from itsm.project.models import Project
from nocode.page.tests.params import SON_POINT
from nocode.page.models import Page


class TestPageComponent(TestCase):
    def setUp(self) -> None:
        project_data = {
            "key": "testprojectv2",
            "name": "testprojectv3",
            "desc": "testproject",
            "owner": {"users": ["admin"]},
            "color": ["#3a84ff", "#6cbaff"],
            "logo": "T",
        }
        Project.objects.create(**project_data)
        for page_data in SON_POINT:
            Page.objects.create(**page_data)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_batch_save(self) -> None:
        page = Page.objects.get(name="page1", type="FUNCTION")
        data = {
            "page_id": page.id,
            "components": [
                {
                    "page_id": page.id,
                    "type": "FUNCTION",
                    "value": 29,
                    "config": {"name": "xxxx", "desc": "zzz"},
                }
            ],
        }

        res = self.client.post(
            "/api/page_design/page_component/batch_save/",
            data,
            content_type="application/json",
        )
        self.assertEqual(res.data["result"], True)
