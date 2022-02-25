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


class TestSuperUserViewSet(TestCase):
    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_superuser_add(self):
        url = "/api/project/system_user/operate_superuser/"
        add_data = {"users": ["tester"], "action": "ADD"}
        add_res = self.client.post(url, data=add_data)

        self.assertEqual(add_res.data["code"], "OK")
        self.assertEqual(add_res.data["message"], "success")
        self.assertEqual(add_res.data["data"][0]["username"], "tester")
        self.assertEqual(add_res.data["data"][0]["is_superuser"], True)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_superuser_list(self):
        self.test_superuser_add()

        url = "/api/project/system_user/"
        list_res = self.client.get(url)
        self.assertEqual(list_res.data["message"], "success")
        self.assertEqual(len(list_res.data["data"]["items"]), 2)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_superuser_delete(self):
        self.test_superuser_list()
        url = "/api/project/system_user/operate_superuser/"
        delete_data = {"action": "DELETE", "users": ["tester"]}
        delete_res = self.client.post(url, data=delete_data)
        self.assertEqual(delete_res.data["code"], "OK")
        self.assertEqual(delete_res.data["message"], "success")
        self.assertEqual(delete_res.data["data"][0]["username"], "tester")
        self.assertEqual(delete_res.data["data"][0]["is_superuser"], False)
