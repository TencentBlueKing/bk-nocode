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


class GradeGenerator:
    """
    meta: {
        "config": {
            "type":,
            "field_key":
            "max": 5/10
        }
    }
    """

    def __init__(self, filed):
        if isinstance(filed["meta"], str):
            meta = json.loads(filed["meta"])
        else:
            meta = filed["meta"]
        self.config = meta.get("config")
        self.filed = filed

    def generate_grade(self, validated_data):
        if self.config["field_key"] and not validated_data.get("key"):
            if float(validated_data[self.config["field_key"]]) >= self.config["max"]:
                return validated_data[self.filed["max"]]
            elif float(validated_data[self.config["field_key"]]) <= 0:
                return 0
            return validated_data[self.config["field_key"]]
        return validated_data[self.filed["key"]]
