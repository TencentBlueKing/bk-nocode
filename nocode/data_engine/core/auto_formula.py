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
from datetime import datetime
from functools import reduce

from nocode.worksheet.exceptions import FormulaInputError


class FormulaGenerator:
    """{
        ...
    "meta": {
        "config": {
            "calculate_type": "number",
            "formula_type": "max/min/.../custom",
            "fields": [
                "fields_1_key",
                "fields_2_key,
            ]
            "value": "{fields_2}+{b}+({b}+{c})"
            "affix": "缀名",
            "affix_type": "0/1"  (0：前缀， 1：后缀)
            "accuracy": num 小数精确度
        },
        or
        {
            "calculate_type": "time,
            "type": "custom",
            "fields": [
                "fields_time_1_key",
                "fields_time_2_key,
            ]
            "value": "start_time-end_time"
            "can_format": true/false,
            "can_affix": true/false,
            "accuracy": time_value/day/hour/minute 时间精确度
        },
    }
    }"""

    def __init__(self, filed):
        if isinstance(filed["meta"], str):
            meta = json.loads(filed["meta"])
        else:
            meta = filed["meta"]
        self.configs = meta.get("config", [])
        self.filed = filed
        self.FORMULA_MAP = {
            "SUM": self.add,
            "MAX": self.max,
            "MIN": self.min,
            "CUSTOM": self.custom,
            "AVERAGE": self.average,
            "PRODUCT": self.product,
            "COUNT": self.count,
            "MEDIAN": self.median,
            "ARGMAX": self.argmax,
        }

    def add(self, params_list):
        return sum(params_list)

    def max(self, params_list):
        return max(params_list)

    def min(self, params_list):
        return min(params_list)

    def average(self, params_list):
        return sum(params_list) / len(params_list)

    def product(self, params_list):
        def func(x, y):
            return x * y

        return reduce(func, params_list)

    def median(self, params_list):
        params_list.sort()
        middle_index = len(params_list) // 2
        return (params_list[middle_index] + params_list[~middle_index]) / 2

    def argmax(self, params_list):
        count_dict = {}
        for item in params_list:
            count_dict[item] = count_dict.get(item, 0) + 1
        count_max = max(count_dict.values())
        most_values = [k for k, v in count_dict.items() if v == count_max]
        return most_values

    def count(self, params_list):
        return len(params_list)

    def custom(self, params_dict):
        """
        用户自定义公式
        """
        formula = self.configs.get("value")
        try:
            res = eval(formula.format_map(params_dict))
        except ZeroDivisionError or Exception:
            raise FormulaInputError()
        return res

    def property_add(self, result):
        # 小数精确
        accuracy = f".{self.configs['accuracy']}f"
        accuracy_result = format(result, accuracy)
        # 缀名增加
        if int(self.configs["affix_type"]) == 1:
            # 增加前缀
            result = "{affix}{accuracy_result}".format(
                affix=self.configs["affix"], accuracy_result=accuracy_result
            )
        else:
            # 增加后缀
            result = "{accuracy_result}{affix}".format(
                affix=self.configs["affix"], accuracy_result=accuracy_result
            )
        return result

    def time_format(self, params, validated_data, sys_time_fields):
        # 指定时间字段
        if params in validated_data:
            params = validated_data[params]
        # 系统时间字段
        if params in sys_time_fields:
            params = sys_time_fields.get(params, datetime.now())
        # 最终返回（常量）
        return params

    def generate_formula_result(self, validated_data, sys_time_fields):
        params_keys = self.configs["fields"]
        if self.configs["calculate_type"] == "number":
            cal_method = self.FORMULA_MAP.get(self.configs["type"].upper())
            if self.configs["type"] == "CUSTOM":
                params_dict = {}
                for key in params_keys:
                    params_dict[key] = validated_data[key]
                result = cal_method(params_dict)
            else:
                params_list = []
                for key in params_keys:
                    params_list.append(validated_data[key])
                result = cal_method(params_list)
            if self.configs["type"].upper() == "ARGMAX":
                data = []
                for num in result:
                    data.append(self.property_add(num))
                return ",".join(data)
            return self.property_add(result)
        else:

            start_time = self.time_format(
                self.configs["start_time"], validated_data, sys_time_fields
            )
            end_time = self.time_format(
                self.configs["end_time"], validated_data, sys_time_fields
            )

            result = f"{end_time} - {start_time}"
            return result
