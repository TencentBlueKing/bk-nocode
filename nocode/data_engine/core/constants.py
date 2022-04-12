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
TYPE_MAPPING = {
    "==": ("", True),
    "!=": ("", False),
    ">": ("__gt", True),
    "<": ("__lt", True),
    ">=": ("__gte", True),
    "<=": ("__lte", True),
    "in": ("__in", True),
    "icontains": ("__icontains", True),
}
ALLOWED_EXPRESSION_CONDITION_KEY = [key for key in TYPE_MAPPING]

CONNECTOR_KEYWORD = "connector"
EXPRESSION_KEYWORD = "expressions"
GROUP_CONNECTOR_KEYWORD = "group_connector"
GROUP_EXPRESSION_KEYWORD = "group_expressions"
ALLOWED_CONDITION_KEY = [
    CONNECTOR_KEYWORD,
    EXPRESSION_KEYWORD,
    GROUP_EXPRESSION_KEYWORD,
    GROUP_CONNECTOR_KEYWORD,
]

TYPE_KEYWORD = "type"
CONDITION_KEYWORD = "condition"
KEY_KEYWORD = "key"
VALUE_KEYWORD = "value"
ALLOWED_EXPRESSION_KEY = [TYPE_KEYWORD, CONDITION_KEYWORD, KEY_KEYWORD, VALUE_KEYWORD]

AND_KEYWORD = "AND"
OR_KEYWORD = "OR"
ALLOWED_CONNECTOR_KEY = [AND_KEYWORD, OR_KEYWORD]

ALLOWED_EXPRESSION_TYPE_KEY = "const"
PK_KEYWORD = ["id", "ids"]
SYS_KEYWORD = ["create_at", "update_at", "creator", "updated_by"]

DAY = "day"
MONTH = "month"
YEAR = "year"
# 按月查询年相隔
YEARS_APART = 3
TIME_VALUE = [DAY, MONTH, YEAR]
