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
from django.db import models, OperationalError

from nocode.data_engine.core.config import DataInstanceConfig
from nocode.data_engine.core.utils import install


class BaseBackend:
    def __init__(self, db_name):
        self.da_name = db_name

    def get_model(self):
        pass

    def install(self, custom_model):
        pass

    def create_table(self):
        pass


class DjangoBackend(BaseBackend):
    """
    django动态创建表backend
    """

    def get_model(self):
        class Meta:  # 模型类的Meta类
            pass

        setattr(Meta, "app_label", DataInstanceConfig.APP_LABEL)  # 更新元类的选项

        FIELDS = {
            "contents": models.JSONField(),
            "create_at": models.DateTimeField(auto_now_add=True),
            "update_at": models.DateTimeField(auto_now=True),
            "creator": models.CharField(max_length=64, null=True, blank=True),
            "updated_by": models.CharField(max_length=64, null=True, blank=True),
            "__str__": lambda self: "%s %s %s %s %s"
            % (
                self.contents,
                self.create_at,
                self.update_at,
                self.creator,
                self.updated_by,
            ),
        }
        for key, value in DataInstanceConfig.OPTIONS.items():
            setattr(Meta, key, value)  # 设置模型的属性
            attrs = {"__module__": self.da_name, "Meta": Meta}  # 添加字段属性

        attrs.update(FIELDS)  # 创建模型类对象
        return type(self.da_name, (models.Model,), attrs)  # 用type动态创建类

    def create_table(self):
        custom_model = self.get_model()
        try:
            install(custom_model)  # 同步到数据库中
        except OperationalError:
            # 表已经存在
            pass
