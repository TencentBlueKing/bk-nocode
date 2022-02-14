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
from django.test import override_settings

from itsm.project.models import Project
from nocode.base.base_tests import MyTestCase
from nocode.test.page.params import CREATE_PROJECT_DATA
from nocode.test.worksheet.params import WORKSHEET_DATA, WORKSHEET_FIELD
from nocode.worksheet.models import WorkSheet
from nocode.worksheet.views.worksheetfield import WorkSheetFieldViewSet


class TestWorkSheetFieldsView(MyTestCase):
    def setUp(self) -> None:
        Project.objects.get_or_create(**CREATE_PROJECT_DATA)
        WorkSheet.objects.get_or_create(**WORKSHEET_DATA)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_batch_save(self):
        url = "/api/worksheet/fields/batch_save/"
        res = self.client.post(
            url, data=WORKSHEET_FIELD, content_type="application/json"
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
