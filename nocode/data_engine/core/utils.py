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
from celery.task import task
from django.db import connection
from django.db.models import Q
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.conf import settings

from nocode.data_engine.core.constants import (
    ALLOWED_CONDITION_KEY,
    CONNECTOR_KEYWORD,
    ALLOWED_CONNECTOR_KEY,
    EXPRESSION_KEYWORD,
    CONDITION_KEYWORD,
    ALLOWED_EXPRESSION_CONDITION_KEY,
    TYPE_KEYWORD,
    ALLOWED_EXPRESSION_TYPE_KEY,
    KEY_KEYWORD,
    PK_KEYWORD,
    VALUE_KEYWORD,
    TYPE_MAPPING,
    ALLOWED_EXPRESSION_KEY,
    SYS_KEYWORD,
)


def install(custom_model):
    """
    动态创建表
    """
    with BaseDatabaseSchemaEditor(connection) as editor:
        editor.create_model(model=custom_model)


@task
def value_reset(key, value, change_format):
    if not int(change_format):
        settings.REDIS_INST.set(key, int(value) - 1)
    else:
        settings.REDIS_INST.set(key, 0)


class ConditionTransfer(object):
    def __init__(self, conditions, for_worksheet=True):
        """
        :param conditions: 筛选条件
        {
            "connector": "and",
            "expressions": [
                {
                    "key": "id",
                    "type": "const",
                    "condition": "==",
                    "value": 1
                },
                {
                    "key": "age",
                    "type": "const",
                    "condition": ">",
                    "value": 18
                }
            ]
        }
        """
        self.conditions = conditions
        self.condition_filter = Q()
        self.for_worksheet = for_worksheet

    def _verify(self):
        """校验器"""
        # 检测 conditions 所含的参数
        for key in self.conditions:
            assert key in ALLOWED_CONDITION_KEY, "Wrong Params in Condition"
        # 检查 Q 的连接方式
        assert (
            self.conditions[CONNECTOR_KEYWORD].upper() in ALLOWED_CONNECTOR_KEY
        ), "Dismatch Type of 'Connector'"
        # 检测 conditions.expressions 的构造
        expressions = self.conditions.get(EXPRESSION_KEYWORD, None)
        assert isinstance(expressions, list) and len(
            expressions
        ), "Expressions cannot be empty"
        # 检测 conditions.expressions 的每个条件的构造
        for expression in expressions:
            assert len(expression) == len(
                ALLOWED_EXPRESSION_KEY
            ), "Wrong number of Params"
            for key, val in expression.items():
                assert key in ALLOWED_EXPRESSION_KEY, "Wrong Params in Expression"
                if key == CONDITION_KEYWORD:
                    assert (
                        val in ALLOWED_EXPRESSION_CONDITION_KEY
                    ), "Dismatch Type of 'Condition'"
                if key == TYPE_KEYWORD:
                    assert val == ALLOWED_EXPRESSION_TYPE_KEY, "Dismatch Type of 'Type'"

    def _expression_connector(self, expression):
        """转换为符合 Q 的元组"""
        key = expression[KEY_KEYWORD]
        if key in PK_KEYWORD:
            key = "id"
        elif key in SYS_KEYWORD:
            pass
        elif key not in PK_KEYWORD and self.for_worksheet:
            key = "contents__{}".format(key)
        condition = expression[CONDITION_KEYWORD]
        value = expression[VALUE_KEYWORD]
        suffix, positive = TYPE_MAPPING[condition]
        q = Q() if positive else ~Q()
        q.children.append(("{}{}".format(key, suffix), value))
        self.condition_filter.add(
            q, self.conditions[CONNECTOR_KEYWORD].upper(), squash=False
        )

    def trans(self):
        """转换器"""
        if not self.conditions:
            return Q()
        self._verify()
        self.condition_filter.connector = self.conditions[CONNECTOR_KEYWORD].upper()
        for expression in self.conditions[EXPRESSION_KEYWORD]:
            self._expression_connector(expression)
        return self.condition_filter
