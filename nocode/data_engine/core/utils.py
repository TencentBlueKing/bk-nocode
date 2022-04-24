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
import ast
import datetime

from celery.task import task
from django.db import connection
from django.db.models import Q
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.conf import settings

from common.log import logger
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
    GROUP_CONNECTOR_KEYWORD,
    GROUP_EXPRESSION_KEYWORD,
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

    def _verify(self, conditions=None):
        """校验器"""
        if not conditions:
            conditions = self.conditions

        # 检测 conditions 所含的参数
        for key in conditions:
            assert key in ALLOWED_CONDITION_KEY, "Wrong Params in Condition"
        # 检查 Q 的连接方式
        if GROUP_CONNECTOR_KEYWORD in conditions:
            assert (
                conditions[GROUP_CONNECTOR_KEYWORD].upper() in ALLOWED_CONNECTOR_KEY
            ), "Dismatch Type of 'Connector'"
        else:
            assert (
                conditions[CONNECTOR_KEYWORD].upper() in ALLOWED_CONNECTOR_KEY
            ), "Dismatch Type of 'Connector'"
        # 检测 condition.group_expressions 下的构造
        if GROUP_EXPRESSION_KEYWORD in conditions:
            for item in conditions.get(GROUP_EXPRESSION_KEYWORD, None):
                self._verify(item)
        # 检测 expressions 的构造
        else:
            expressions = conditions.get(EXPRESSION_KEYWORD, None)
            if isinstance(expressions, list) and not expressions:
                return
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
                        assert (
                            val == ALLOWED_EXPRESSION_TYPE_KEY
                        ), "Dismatch Type of 'Type'"
        assert (
            self.conditions[CONNECTOR_KEYWORD].upper() in ALLOWED_CONNECTOR_KEY
        ), "Dismatch Type of 'Connector'"
        # 检测 conditions.expressions 的构造
        expressions = self.conditions.get(EXPRESSION_KEYWORD, None)
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
        if condition == "in":
            if isinstance(expression[VALUE_KEYWORD], str):
                value = value.split(",")
        suffix, positive = TYPE_MAPPING[condition]
        q = Q() if positive else ~Q()
        q.children.append(("{}{}".format(key, suffix), value))
        self.condition_filter.add(
            q, self.conditions[CONNECTOR_KEYWORD].upper(), squash=False
        )

    def _group_expression_connector(self, expression, condition_filter, conditions):

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
        if condition == "in":
            if isinstance(expression[VALUE_KEYWORD], str):
                value = value.split(",")
        suffix, positive = TYPE_MAPPING[condition]
        q = Q() if positive else ~Q()
        q.children.append(("{}{}".format(key, suffix), value))
        condition_filter.add(q, conditions[CONNECTOR_KEYWORD].upper(), squash=False)
        return condition_filter

    def _group_trans(self, conditions, condition_filter):
        for expression in conditions[EXPRESSION_KEYWORD]:
            self._group_expression_connector(expression, condition_filter, conditions)

    def trans(self):
        """转换器"""
        if not self.conditions:
            return Q()
        self._verify()
        if GROUP_CONNECTOR_KEYWORD not in self.conditions:
            self.condition_filter.connector = self.conditions[CONNECTOR_KEYWORD].upper()
            for expression in self.conditions[EXPRESSION_KEYWORD]:
                self._expression_connector(expression)
        else:
            self.condition_filter.connector = self.conditions[
                GROUP_CONNECTOR_KEYWORD
            ].upper()
            for condition in self.conditions[GROUP_EXPRESSION_KEYWORD]:
                condition_filter = Q()
                condition_filter.connector = condition[CONNECTOR_KEYWORD].upper()
                self._group_trans(condition, condition_filter)
                self.condition_filter.add(
                    condition_filter,
                    self.conditions[GROUP_CONNECTOR_KEYWORD].upper(),
                    squash=False,
                )
        return self.condition_filter


def compute_time_range(time_range):
    """

    time_range: 时间范围

    all 全部

    current_day: 当天
    current_week: 本周
    current_month: 本月
    current_year: 本年度

    last_day: 昨天
    last_week: 上周
    last_month: 上个月
    last_year: 上一年
    """

    now = datetime.date.today()

    time_range_conditions = Q()

    compute_map = {
        "current_day": datetime.date.today(),
        "current_week": now - datetime.timedelta(days=now.weekday()),
        "current_month": now.replace(day=1),
        "current_year": now.replace(month=1, day=1),
    }

    value = compute_map.get(time_range)

    if isinstance(value, tuple):
        # 未后面时间区间做扩展
        pass
    else:
        time_range_conditions.add(Q(create_at__gte=value), Q.AND, squash=False)

    return time_range_conditions


def value_to_list(upload_keys, queryset):
    if upload_keys:
        for item in queryset:
            for field in upload_keys:
                if item[field]:
                    # 列表字符串转换成列表
                    try:
                        item[field] = ast.literal_eval(item[field])
                    except SyntaxError:
                        logger.warn(f"{field} -> 参数传输有误 {item[field]}")
                        continue
                else:
                    item[field] = []
    return queryset
