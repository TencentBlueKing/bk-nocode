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
import copy
import os
import time

from django.db import transaction, IntegrityError
from django.db import connection

from rest_framework import serializers

from common.log import logger
from nocode.data_engine.core.auto_formula import FormulaGenerator
from nocode.data_engine.core.auto_grade import GradeGenerator
from nocode.data_engine.core.auto_number import NumberGeneratorDispatcher
from nocode.data_engine.core.db import DjangoBackend
from nocode.data_engine.core.serializer import SerializerDispatcher
from nocode.data_engine.handlers.module_handlers import WorkSheetHandler

CURRENT_MYSQL_VERSION = int(os.environ.get("MYSQL_VERSION", 5))


class BaseIndexManager:
    def __init__(self, db_name):
        self.db_name = db_name

    def create_unique_index(self, key):
        pass

    def drop_unique_index(self, key):
        pass


class Mysql57IndexManager(BaseIndexManager):
    def create_unique_index(self, key):
        index_name = "{0}_contents_{1}".format(self.db_name, key)

        table_name = "worksheet_{}".format(self.db_name)

        # 新增一列
        add_column_sql = "ALTER TABLE {0} ADD COLUMN {1} varchar(128) GENERATED ALWAYS AS (contents->'$.{2}');".format(
            table_name, key, key
        )

        # 创建一个索引
        create_index_sql = "CREATE UNIQUE INDEX {0} ON {1}({2});".format(
            index_name, table_name, key
        )

        start = time.time()

        logger.info("start: {}".format(start))

        logger.info("add_column_sql is {}".format(add_column_sql))
        logger.info("create_index_sql is {}".format(create_index_sql))

        try:
            cursor = connection.cursor()
            logger.info("get cursor: {}".format(time.time() - start))
            cursor.execute(add_column_sql)
            logger.info("execute add_column_sql: {}".format(time.time() - start))
            cursor.execute(create_index_sql)
            logger.info("execute create_index_sql: {}".format(time.time() - start))
        except IntegrityError as e:
            logger.info("数据库索引创建失败，已回滚，db_name={}, key={}".format(self.db_name, key))
            self.drop_unique_index(key)
            raise e

    def drop_unique_index(self, key):

        table_name = "worksheet_{}".format(self.db_name)
        # 删除一列
        delete_column_sql = "ALTER TABLE {0} DROP COLUMN {1};".format(table_name, key)
        cursor = connection.cursor()
        cursor.execute(delete_column_sql)


class Mysql8IndexManager(BaseIndexManager):
    def create_unique_index(self, key):
        index_name = "{0}_contents_{1}".format(self.db_name, key)

        table_name = "worksheet_{}".format(self.db_name)

        sql = "CREATE UNIQUE INDEX {0} ON {1}( ( cast( contents->>'$.{2}' as char(128) ) ) );".format(
            index_name, table_name, key
        )
        # 真正的原生sql,
        cursor = connection.cursor()
        cursor.execute(sql)

    def drop_unique_index(self, key):
        index_name = "{0}_contents_{1}".format(self.db_name, key)

        table_name = "worksheet_{}".format(self.db_name)

        sql = "DROP INDEX {0} on {1};".format(index_name, table_name)
        cursor = connection.cursor()
        cursor.execute(sql)


class BaseTableManager:
    def __init__(self, table_name):
        self.table_name = table_name

    def drop_table(self):
        pass


class TableManager(BaseTableManager):
    def drop_table(self):
        sql = "DROP TABLE {};".format(self.table_name)
        cursor = connection.cursor()
        cursor.execute(sql)


class DataManager:
    def __init__(self, worksheet_id):
        self.worksheet_id = worksheet_id
        self.index_manager = Mysql57IndexManager
        if CURRENT_MYSQL_VERSION == 8:
            self.index_manager = Mysql8IndexManager

    @property
    def worksheet(self):
        return self.handler.get_instance()

    @property
    def handler(self):
        return WorkSheetHandler(worksheet_id=self.worksheet_id)

    @property
    def fields(self):
        return self.handler.get_fields()

    @property
    def db_name(self):
        return "{0}_{1}".format(self.worksheet.project_key.lower(), self.worksheet.key)

    @property
    def model(self):
        return DjangoBackend(self.db_name).get_model()

    def serializer_validate(self, data):
        serializer_class = SerializersGenerator(self.fields).build_serializers()(
            data=data
        )
        serializer_class.is_valid(raise_exception=True)
        validated_data = serializer_class.validated_data
        return validated_data

    def get_queryset(self):
        return self.model.objects.all()

    def get(self, pk):
        return self.model.objects.get(id=pk)

    def add(self, data, creator=None):
        validated_data = self.serializer_validate(data)
        with transaction.atomic():
            # 生成一个对象
            obj = self.model()
            obj.contents = validated_data
            obj.creator = creator
            obj.save()

            # 生成编号
            data = self.add_auto_number(validated_data)
            if data:
                obj.contents.update(data)
                obj.save()

            # 生成评分
            data = self.add_auto_grade(validated_data)
            if data:
                obj.contents.update(data)
                obj.save()

            # 存在公式控件，数值计算
            data = self.add_formula_result(validated_data, obj)
            if data:
                obj.contents.update(data)
                obj.save()

        return obj

    def add_auto_number(self, validated_data):
        data = {}
        fields = self.get_auto_number_fields()
        for field in fields:
            data[field["key"]] = self.generate_number(
                field, validated_data=validated_data
            )
        return data

    def add_auto_grade(self, validated_data):
        data = {}
        fields = self.get_auto_grade_fields()
        for field in fields:
            data[field["key"]] = self.generate_grade(
                field, validated_data=validated_data
            )
        return data

    def get_auto_grade_fields(self):
        return [field for field in self.fields if field["type"] == "GRADE"]

    def generate_grade(self, field, validated_data):
        return GradeGenerator(field).generate_grade(validated_data=validated_data)

    def generate_number(self, field, validated_data):
        return NumberGeneratorDispatcher(
            field, validated_data=validated_data
        ).generate_number()

    def get_auto_number_fields(self):
        return [field for field in self.fields if field["type"] == "AUTO-NUMBER"]

    def add_formula_result(self, validated_data, record):
        data = {}
        fields = self.get_formula_fields()
        if not fields:
            return data
        for field in fields:
            result = self.generate_formula_result(field, validated_data, record)
            data.setdefault(field["key"], result)
        return data

    def get_formula_fields(self):
        return [field for field in self.fields if field["type"] == "FORMULA"]

    def generate_formula_result(self, field, validated_data, record):
        return FormulaGenerator(field).generate_formula_result(validated_data, record)

    def delete(self, pk):
        with transaction.atomic():
            # 生成一个对象
            self.model.objects.get(id=pk).delete()

    def update(self, pk, data, updated_by=None):
        validated_data = self.serializer_validate(data)
        with transaction.atomic():
            # 生成一个对象
            obj = self.model.objects.get(id=pk)
            obj.contents = self.update_content(obj.contents, validated_data, obj)
            obj.updated_by = updated_by
            obj.save()

    def update_content(self, obj_contents, validated_data, obj):
        # content数据更新
        contents = copy.deepcopy(obj_contents)
        # 兼容隐藏字段直接采用原数据
        for key, value in validated_data.items():
            if not value:
                continue
            contents[key] = value
        # 计算控件重新计算
        data = self.add_formula_result(contents, obj)
        if data:
            contents.update(data)
        return contents

    def create_unique_index(self, key):
        self.index_manager(self.db_name).create_unique_index(key)

    def drop_unique_index(self, key):
        self.index_manager(self.db_name).drop_unique_index(key)

    def drop_table(self):
        table_name = "worksheet_{}".format(self.db_name)
        TableManager(table_name).drop_table()


class SerializersGenerator:
    def __init__(self, fields):
        self.fields = fields

    def build_serializers(self):
        attrs = {}
        for filed in self.fields:
            serializer = SerializerDispatcher(filed).get_serializer()
            attrs[filed["key"]] = serializer

        return type("AutoSerializers", (serializers.Serializer,), attrs)
