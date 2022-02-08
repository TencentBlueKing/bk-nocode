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
from nocode.base.base_tests import MyTestCase
from nocode.worksheet.models import WorkSheet
from nocode.worksheet.views.worksheet import WorkSheetViewSet


class TestWorkSheetView(MyTestCase):
    def setUp(self) -> None:
        WORKSHEET_DATA = {
            "id": 1,
            "creator": "admin",
            "create_at": "2021-09-18 15:51:22",
            "update_at": "2021-09-18 15:51:22",
            "updated_by": "admin",
            "is_deleted": False,
            "name": "这是一张测试工作表",
            "desc": "test_worksheet",
            "key": "test_worksheet",
            "project_key": "test-m",
        }

        WorkSheet.objects.get_or_create(**WORKSHEET_DATA)

    swagger_test_view = WorkSheetViewSet

    actions_exempt = ["create", "destroy", "list", "update", "partial_update"]
