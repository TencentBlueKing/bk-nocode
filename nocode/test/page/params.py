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

CREATE_PROJECT_DATA = {
    "key": "test",
    "creator": "admin",
    "name": "test",
    "desc": "test",
    "color": json.dumps(["#3a84ff", "#6cbaff"]),
    "logo": "T",
}

CREATE_PAGE_1 = {
    "project_key": CREATE_PROJECT_DATA["key"],
    "name": "page1",
    "type": "FUNCTION",
}
CREATE_PAGE_2 = {
    "project_key": CREATE_PROJECT_DATA["key"],
    "name": "page2",
    "type": "LIST",
}
CREATE_PAGE_3 = {
    "project_key": CREATE_PROJECT_DATA["key"],
    "name": "page3",
    "type": "SHEET",
}

SON_POINT = [CREATE_PAGE_1, CREATE_PAGE_2, CREATE_PAGE_3]

NEW_ORDER = []
