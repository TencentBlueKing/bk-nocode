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
from rest_framework import serializers


class BaseGenerator:
    serializer_field_class = None

    def __init__(self, filed):
        self.filed = filed

    def get_serializer(self):
        params = self._build_serializer_params()
        return self.serializer_field_class(**params)

    def _build_serializer_params(self):
        params = {"help_text": self.filed["name"]}
        if self.filed["validate_type"] == "OPTION":
            params["required"] = False
            params["allow_null"] = True
            params["allow_blank"] = True
            params["default"] = self.filed["default"]
        return params


class IntGenerator(BaseGenerator):
    serializer_field_class = serializers.IntegerField

    def _build_serializer_params(self):
        params = {"help_text": self.filed["name"]}
        if self.filed["validate_type"] == "OPTION":
            params["required"] = False
            params["allow_null"] = True
            params["default"] = self.filed["default"]
        return params


class CharGenerator(BaseGenerator):
    serializer_field_class = serializers.CharField


class DataGenerator(BaseGenerator):
    serializer_field_class = serializers.CharField


class ChoiceGenerator(BaseGenerator):
    serializer_field_class = serializers.ChoiceField

    def _build_serializer_params(self):
        params = {}
        if self.filed["source_type"] == "CUSTOM":
            params["choices"] = self._build_choice_params()
        else:
            self.serializer_field_class = serializers.CharField
        if self.filed["validate_type"] == "OPTION":
            params["required"] = False
            params["allow_blank"] = True
            params["default"] = self.filed["default"]
        return params

    def _build_choice_params(self):
        """
        将字段choice转换成序列化起choice约束
        """
        choices = []
        for choice in self.filed["choice"]:
            choices.append((choice.get("key"), choice.get("name")))

        return choices


class ListGenerator(BaseGenerator):
    serializer_field_class = serializers.ListField

    def _build_serializer_params(self):
        params = {"help_text": self.filed["name"]}
        if self.filed["validate_type"] == "OPTION":
            params["required"] = False
            params["allow_null"] = True
            params["default"] = []
        return params


class SerializerDispatcher:
    # TYPE_CHOICES = [
    #     ("STRING", "单行文本"),
    #     ("TEXT", "多行文本"),
    #     ("INT", "数字"),
    #     ("DATE", "日期"),
    #     ("DATETIME", "时间"),
    #     ("DATETIMERANGE", "时间间隔"),
    #     ("TABLE", "表格"),
    #     ("SELECT", "单选下拉框"),
    #     ("INPUTSELECT", "可输入单选下拉框"),
    #     ("MULTISELECT", "多选下拉框"),
    #     ("CHECKBOX", "复选框"),
    #     ("RADIO", "单选框"),
    #     ("MEMBER", "单选人员选择"),
    #     ("MEMBERS", "多选人员选择"),
    #     ("RICHTEXT", "富文本"),
    #     ("FILE", "附件上传"),
    #     ("CUSTOMTABLE", "自定义表格"),
    #     ("TREESELECT", "树形选择"),
    #     ("LINK", "链接"),
    #     ("CUSTOM-FORM", "自定义表单"),
    #     ("CASCADE", "级联"),
    # ]

    def __init__(self, filed):
        self.filed = filed

    _GENERATOR_MAP = {
        "INT": IntGenerator,
        "DATE": DataGenerator,
        "SELECT": ChoiceGenerator,
        "RADIO": ChoiceGenerator,
        "TABLE": ListGenerator,
    }

    def get_serializer(self):
        generator = self._GENERATOR_MAP.get(self.filed["type"], CharGenerator)
        return generator(self.filed).get_serializer()
