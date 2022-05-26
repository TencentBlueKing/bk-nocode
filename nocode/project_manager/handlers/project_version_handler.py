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

import uuid

from django.db import transaction

from nocode.base.base_handler import APIModel
from nocode.data_engine.core.managers import DataManager
from nocode.project_manager.exceptions import ProjectVersionDoesNotExists
from nocode.project_manager.handlers.module_handler import (
    ProjectConfigVersionGenerator,
    PageVersionGenerator,
    PageComponentVersionGenerator,
    WorkSheetVersionGenerator,
    WorkSheetFieldVersionGenerator,
    ProjectModuleHandler,
    WorkSheetFieldModuleHandler,
    WorkSheetModuleHandler,
    WorkSheetEventVersionGenerator,
)
from nocode.project_manager.handlers.project_white_handler import white_token_generate
from nocode.project_manager.models import ProjectVersion


class ProjectVersionModelHandler(APIModel):
    def __init__(self, project_key, version_number=None, log_handler=None):
        self.project_key = project_key
        self.version_number = version_number
        self.log_handler = log_handler
        self.obj = None
        self.single_page = None

    def _get_instance(self):
        try:
            obj = ProjectVersion.objects.get(
                project_key=self.project_key, version_number=self.version_number
            )
        except ProjectVersion.DoesNotExist:
            raise ProjectVersionDoesNotExists()
        return obj

    @property
    def instance(self):
        if self.obj is None:
            self.obj = self._get_instance()
        return self.obj

    def create_version(self):
        """
        创建一个版本
        """
        self.log_handler.create_log("开始创建应用版本快照")
        project_config = ProjectConfigVersionGenerator().create_version(
            self.project_key
        )
        self.log_handler.create_log("应用配置版本快照创建完成")
        page = PageVersionGenerator().create_version(self.project_key)
        self.log_handler.create_log("应用页面版本快照创建完成")
        page_component = PageComponentVersionGenerator().create_version(
            self.project_key
        )
        self.log_handler.create_log("页面组件版本快照创建完成")
        worksheet = WorkSheetVersionGenerator().create_version(self.project_key)
        self.log_handler.create_log("工作表版本快照创建完成")
        worksheet_events = WorkSheetEventVersionGenerator().create_version(
            self.project_key
        )
        self.log_handler.create_log("工作表触发事件版本快照创建完成")
        worksheet_field = WorkSheetFieldVersionGenerator().create_version(
            self.project_key
        )
        self.log_handler.create_log("工作表字段版本快照创建完成")
        version_number = uuid.uuid4().hex

        self.log_handler.create_log("正在创建最终的应用版本")
        with transaction.atomic():
            version = ProjectVersion.objects.create(
                project_config=project_config,
                page=page,
                page_component=page_component,
                worksheet=worksheet,
                worksheet_field=worksheet_field,
                worksheet_event=worksheet_events,
                version_number=version_number,
                project_key=self.project_key,
            )
        self.log_handler.create_log("应用版本创建完成, 版本号为:{}".format(version_number))

        return version

    def get_version(self, version_number):
        return ProjectVersion.objects.get(
            project_key=self.project_key, version_number=version_number
        )

    def get_project_config(self):
        return self.instance.project_config

    def get_page(self, page_id=None, page=None, return_page=None):
        pages = self.instance.page if not page else page
        page = None
        if page_id:
            for item in pages:
                if item["id"] == int(page_id):
                    self.single_page = item
                    return
                if item["children"]:
                    self.get_page(
                        page_id=page_id, page=item["children"], return_page=page
                    )
        return pages if not page_id else self.single_page

    def get_page_component(self, page_id):
        components = self.instance.page_component.get(page_id)
        page = self.get_page(page_id=page_id)
        component_list = page.get("component_list", [])

        def get_children_in_container(component_data, data_struct):
            if component_data["type"] in ["FUNCTION_GROUP", "LINK_GROUP"]:
                component_data.setdefault(
                    "children",
                    [
                        data_struct[child]
                        for child in component_data["config"]["component_order"]
                    ],
                )
            return component_data

        # 重新构造组件数据结构
        data_struct = {}
        for item in components:
            data_struct.setdefault(int(item["id"]), item)
        return_components = []
        for item in components:
            if item["type"] not in ["FUNCTION_GROUP", "LINK_GROUP", "TAB"]:
                return_components.append(item)
                continue

            if item["type"] == "TAB":
                component_ids_in_tab = item["config"]["component_order"]
                component_in_tab = []
                for component_id_tab in component_ids_in_tab:
                    component_data = get_children_in_container(
                        data_struct[component_id_tab], data_struct
                    )
                    component_in_tab.append(component_data)
                item.setdefault("children", component_in_tab)

            item = get_children_in_container(item, data_struct)
            return_components.append(item)
        return (
            [data_struct[item] for item in component_list]
            if component_list
            else return_components
        )

    def get_worksheet(self):
        return self.instance.worksheet

    def get_worksheet_fields(self, worksheet_id):
        worksheet_fields = self.instance.worksheet_field.get(worksheet_id)
        for field in worksheet_fields:
            # 关联数据员的生成白名单token
            if field["source_type"] == "WORKSHEET":
                white_token_generate(field)
        return worksheet_fields


class WorksheetIndexHandler:
    def __init__(self, project_key, log_handler):
        self.project_key = project_key
        self.log_handler = log_handler

    def create_unique_index(self, worksheet_id, worksheet_field):

        manager = DataManager(worksheet_id=worksheet_id)

        self.log_handler.create_log(
            "检测到字段[{}]唯一性索引发生了变化, 即将开始创建唯一性索引 ".format(worksheet_field.name)
        )
        try:
            manager.create_unique_index(worksheet_field.key)
        except Exception as e:
            self.log_handler.create_log(
                "字段[{}]唯一性索引创建失败, error={}".format(worksheet_field.name, e)
            )
            raise e

    def drop_unique_index(self, worksheet_id, worksheet_field):

        manager = DataManager(worksheet_id=worksheet_id)

        self.log_handler.create_log(
            "检测到字段[{}]唯一性索引发生了变化, 即将开始删除唯一性索引 ".format(worksheet_field.name)
        )
        try:
            manager.drop_unique_index(worksheet_field.key)
        except Exception as e:
            self.log_handler.create_log(
                "字段[{}]唯一性索引删除失败, error={} ".format(worksheet_field.name, e)
            )
            err_message = str(e)
            if (
                err_message.startswith("(1091")
                and "check that column/key exists" in err_message
            ):
                return
            raise e

    def migrate_old_worksheet(self, worksheet_id, fields):
        """
        对于旧工作表的改动，需要做三件事,
        1. 对于已有的字段新增唯一性约束
        2. 对于新增的唯一性约束
        3. 对于被删除的字段需要删除索引
        """

        self.log_handler.create_log(
            "即将开始迁移工作表，worksheet_id={}... ".format(worksheet_id)
        )

        fields_map = {int(field["id"]): field for field in fields}

        worksheet_filed_module_handler = WorkSheetFieldModuleHandler(worksheet_id)

        worksheet_fields = worksheet_filed_module_handler.fields()

        for worksheet_field in worksheet_fields:
            if worksheet_field.id in fields_map:
                # 如果字段修改为唯一性索引
                if (
                    worksheet_field.unique
                    and not fields_map[worksheet_field.id]["unique"]
                ):
                    self.create_unique_index(worksheet_id, worksheet_field)
                elif (
                    not worksheet_field.unique
                    and fields_map[worksheet_field.id]["unique"]
                ):
                    self.drop_unique_index(worksheet_id, worksheet_field)
            else:
                if worksheet_field.unique:
                    self.create_unique_index(worksheet_id, worksheet_field)

        worksheet_deleted_fields = worksheet_filed_module_handler.deleted_fields()

        self.log_handler.create_log("检测到有些字段已经被删除, 即将开始删除对应的唯一性索引...")
        for delete_field in worksheet_deleted_fields:
            if delete_field.id in fields_map:
                if fields_map.get(delete_field.id).get("unique", False):
                    self.drop_unique_index(worksheet_id, delete_field)

    def migrate_new_worksheet(self, worksheet_id):
        """
        对于新建的表, 对于唯一性字段, 需要创建索引
        """
        worksheet_fields = WorkSheetFieldModuleHandler(
            worksheet_id=worksheet_id
        ).fields()
        for worksheet_field in worksheet_fields:
            if worksheet_field.unique:
                self.create_unique_index(worksheet_id, worksheet_field)

    def migrate_worksheet_fields(self):

        self.log_handler.create_log("正在准备迁移工作表...")

        project_module_handler = ProjectModuleHandler(self.project_key)

        self.log_handler.create_log("正在获取当前应用的版本号...")
        try:
            current_version = project_module_handler.instance.version_number
            self.log_handler.create_log(
                "获取成功 current_version={}...".format(current_version)
            )
            # 更新索引
            project_version_handler = ProjectVersionModelHandler(
                self.project_key, version_number=current_version
            )
            fields = project_version_handler.instance.worksheet_field
            self.log_handler.create_log(
                "正在获取字段信息，获取到{}个工作表的字段信息...".format(len(fields))
            )
        except Exception:
            self.log_handler.create_log("检测到应用为第一次发布...")
            fields = {}

        worksheet_ids = WorkSheetModuleHandler(self.project_key).ids()
        self.log_handler.create_log(
            "正在当前应用下的工作表，worksheet_ids={}...".format(worksheet_ids)
        )

        for worksheet_id in worksheet_ids:
            # 说明是已有字段发生变化
            if str(worksheet_id) in fields.keys():
                self.log_handler.create_log(
                    "检测到worksheet_id={}的工作表可能发生了变化，正在准备迁移最新的字段配置信息".format(worksheet_id)
                )
                self.migrate_old_worksheet(worksheet_id, fields.get(str(worksheet_id)))
            else:
                self.log_handler.create_log(
                    "检测到worksheet_id={}的工作表是一张新的工作表，正在准备迁移最新的字段配置信息".format(
                        worksheet_id
                    )
                )
                # 说明是一张新表
                self.migrate_new_worksheet(worksheet_id)


class WorkSheetMigrateHandler:
    def __init__(self, project_key, log_handler):
        self.project_key = project_key
        self.log_handler = log_handler

    def drop_table(self, deleted_worksheet):
        self.log_handler.create_log(
            "检测到一张工作表被删除，正在准备删除对应的工作表，worksheet_id={}, name={}".format(
                deleted_worksheet.id, deleted_worksheet.name
            )
        )
        try:
            manager = DataManager(worksheet_id=deleted_worksheet.id)
            manager.drop_table()
        except Exception as e:
            err_message = str(e)
            if err_message.startswith("(1051") and "Unknown table" in err_message:
                return

    def migrate_worksheet(self):
        deleted_worksheets = WorkSheetModuleHandler(
            self.project_key
        ).deleted_worksheets()
        for deleted_worksheet in deleted_worksheets:
            self.drop_table(deleted_worksheet)
