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
import datetime

from django.db import transaction
from pypinyin import lazy_pinyin

from nocode.base.base_handler import APIModel
from nocode.worksheet.exceptions import (
    WorkSheetFieldDoesNotExist,
    CreateUniqueIndexError,
)
from nocode.worksheet.handlers.worksheet_handler import WorkSheetModelHandler
from nocode.worksheet.models import WorkSheetField
from nocode.worksheet.tasks import migrate_service


class WorkSheetFieldModelHandler(APIModel):
    def __init__(self, worksheet_field_id=None):
        self.worksheet_field_id = worksheet_field_id
        self.obj = None
        super(WorkSheetFieldModelHandler, self).__init__()

    def _get_instance(self):
        try:
            obj = WorkSheetField.objects.get(id=self.worksheet_field_id)
        except WorkSheetField.DoesNotExist:
            raise WorkSheetFieldDoesNotExist("没有工作表字段")
        return obj

    @property
    def all_worksheet_field(self):
        return WorkSheetField.objects.all()

    def filter(self, *args, **kwargs):
        return self.all_worksheet_field.filter(*args, **kwargs)

    @property
    def instance(self):
        if self.obj is None:
            self.obj = self._get_instance()
        return self.obj

    def get_delete_fields(self, worksheet_id):
        return WorkSheetField._objects.filter(
            worksheet_id=worksheet_id, is_deleted=True
        )

    def get_fields_by_worksheet(self, worksheet_id):
        return WorkSheetField.objects.filter(worksheet_id=worksheet_id)


class WorkSheetFieldIndexHandler:
    """
    负责管理所有的索引创建删除
    """

    @classmethod
    def generate_key(cls, validated_data):

        name = validated_data["name"]
        worksheet_id = validated_data["worksheet_id"]

        key = "_".join(lazy_pinyin(name))

        # 如果数据库中已经存在同名的key，则走版本控制
        if WorkSheetField._objects.filter(
            key=key, worksheet_id=worksheet_id, is_deleted__in=[0, 1]
        ).exists():
            # 目前的业务场景，99足够用了
            for version in range(1, 99):
                new_key = "{0}_{1}".format(key, version)
                if not WorkSheetField._objects.filter(
                    key=new_key, worksheet_id=worksheet_id, is_deleted__in=[0, 1]
                ).exists():
                    return new_key

        return key

    @classmethod
    def is_support_unique_index(cls, validated_data):
        support_unique_index = ["STRING", "INT", "DATETIME", "DATE", "DATETIMERANGE"]
        if (
            validated_data["unique"]
            and validated_data["type"] not in support_unique_index
        ):
            raise CreateUniqueIndexError(
                "{}不允许被设置为唯一性约束".format(validated_data["type"])
            )


class WorkSheetFieldBatchModelHandler:
    def __init__(self, worksheet_id):
        self.worksheet_id = worksheet_id

    def save_data(self, item, context):
        from nocode.worksheet.serializers.worksheetfiled import WorkSheetFieldSerializer

        if item.get("api_instance_id") is None:
            item["api_instance_id"] = 0
        key = WorkSheetFieldIndexHandler.generate_key(item)
        WorkSheetFieldIndexHandler.is_support_unique_index(item)
        item["key"] = key
        serializer = WorkSheetFieldSerializer(data=item, context=context)
        serializer.is_valid(raise_exception=True)
        return WorkSheetField.objects.create(**serializer.validated_data).id

    def get_order_queryset(self):
        fields = WorkSheetModelHandler(self.worksheet_id).instance.fields
        if len(fields) == 0:
            return WorkSheetField.objects.filter(worksheet_id=self.worksheet_id)
        # 按照指定的ID返回, 后续性能如果出现问题，则修复在应用层做重排序
        ordering = "FIELD(`id`, %s)" % ",".join(str(field_id) for field_id in fields)
        queryset = WorkSheetField.objects.filter(
            worksheet_id=self.worksheet_id, id__in=fields
        ).extra(select={"ordering": ordering}, order_by=("ordering",))
        return queryset

    def update_data(self, item, context):
        from nocode.worksheet.serializers.worksheetfiled import WorkSheetFieldSerializer

        if item.get("api_instance_id") is None:
            item["api_instance_id"] = 0
        instance = WorkSheetField.objects.get(id=item["id"])
        # 如果之前不是唯一性索引，修改成为唯一性索引，则创建
        if not instance.unique and item["unique"]:
            WorkSheetFieldIndexHandler.is_support_unique_index(item)
        item.setdefault("update_at", datetime.datetime.now())
        serializer = WorkSheetFieldSerializer(data=item, context=context)
        serializer.is_valid(raise_exception=True)
        for key, value in serializer.validated_data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        instance.save()

    def delete(self, remove_ids):
        WorkSheetField.objects.filter(id__in=remove_ids).delete()

    def batch_save(self, data, context):

        current_ids = []
        fields = []

        with transaction.atomic():
            # 1. 分类，分出已有的数据和新增的数据
            for item in data:
                if item["id"] is not None:
                    current_ids.append(item["id"])
                    fields.append(item["id"])
                    self.update_data(item, context)
                else:
                    worksheet_field_id = self.save_data(item, context)
                    fields.append(worksheet_field_id)
                    current_ids.append(worksheet_field_id)

            all_ids = set(
                WorkSheetField.objects.filter(
                    worksheet_id=self.worksheet_id
                ).values_list("id", flat=True)
            )

            remove_ids = all_ids - set(current_ids)
            self.delete(remove_ids)

            worksheet_handler = WorkSheetModelHandler(self.worksheet_id)
            worksheet_handler.update_fields(fields)

        migrate_service.apply_async((self.worksheet_id,), countdown=2)
        return self.get_order_queryset()
