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
import os
import copy
from datetime import datetime

from django.conf import settings
from django.db import transaction

from itsm.component.constants import (
    ADD_STATE,
    UPDATE_STATE,
    DELETE_STATE,
    VALUE_FROM_FIELD,
    DATA_PROC_STATE,
    NORMAL_STATE,
    DETAIL_STATE,
    EXPORT_STATE,
)
from itsm.service.handler.service_handler import ServiceCatalogHandler
from itsm.service.models import Service, CatalogService
from itsm.workflow.models import Workflow, Field
from nocode.base.basic import ignore_fields_type
from nocode.data_engine.handlers.module_handlers import WorkSheetHandler
from nocode.worksheet.handlers.worksheet_field_handler import WorkSheetFieldModelHandler


class WorkFlowInit(object):
    def __init__(self, worksheet_id, action):
        """
        初始化对象内容
        """
        self.workflow_id = 0
        self.worksheet_id = worksheet_id
        self.worksheet_handler = WorkSheetHandler(self.worksheet_id)
        self.worksheet = self.worksheet_handler.get_instance()
        self.action = action

    def build_conditions(self):
        """
        构造 id 匹配
        """
        conditions = {
            "connector": "and",
            "expressions": [
                {
                    "key": "id",
                    "type": VALUE_FROM_FIELD,
                    "condition": "==",
                    "value": "${param_%s}" % ("id",),
                }
            ],
        }
        if self.action == DELETE_STATE:
            conditions["connector"] = "or"
            conditions["expressions"].append(
                {
                    "key": "ids",
                    "type": VALUE_FROM_FIELD,
                    "condition": "in",
                    "value": "${param_%s}" % ("ids",),
                }
            )
        return conditions

    def update_fields_info(self, raw_field):
        data = {}
        field_ids = []
        # 生成标题字段
        field_data = copy.deepcopy(raw_field)
        # 为更新删除生成 id 字段
        if self.action in (UPDATE_STATE, DELETE_STATE):
            field_data = copy.deepcopy(raw_field)
            field_data.update(
                {
                    "id": 2,
                    "type": "INT",
                    "source": "CUSTOM",
                    "key": "id",
                    "name": "id",
                    "state_id": "",
                    "is_builtin": True,
                    "workflow_id": self.workflow_id,
                }
            )
            data[2] = field_data
            field_ids.append(2)
        if self.action == DELETE_STATE:
            field_data = copy.deepcopy(raw_field)
            field_data.update(
                {
                    "id": 3,
                    "type": "TEXT",
                    "source": "CUSTOM",
                    "key": "ids",
                    "name": "ids",
                    "state_id": "",
                    "is_builtin": True,
                    "workflow_id": self.workflow_id,
                }
            )
            data[3] = field_data
            field_ids.append(3)
        return data, field_ids

    def build_extras(self):
        """
        构造 extras 字段
        """
        extras = {
            "dataManager": {"action": self.action, "worksheet_id": self.worksheet_id}
        }
        if self.action in (UPDATE_STATE, DELETE_STATE):
            extras["dataManager"]["conditions"] = self.build_conditions()
        return extras

    def update_workflow_info(self, data):
        now = datetime.now()
        data["name"] = "worksheet_{}_{}".format(self.worksheet.key, self.action)
        data["workflow_id"] = self.workflow_id
        data["version_number"] = now.strftime("%Y%m%d%H%M%S")
        return data

    def update_states_info(self, states, field_ids):
        data = {}
        for state_id, val in states.items():
            data[state_id] = val
            data[state_id]["key"] = "{}_{}_{}".format(
                self.worksheet.key, self.action, val["name"]
            )
            data[state_id]["workflow"] = self.workflow_id
            if state_id == "2":
                data[state_id]["fields"] = field_ids
            if state_id == "4":
                data[state_id]["extras"] = self.build_extras()
        return data

    def update_transition_info(self, transitions):
        data = {}
        for tran_id, val in transitions.items():
            data[tran_id] = val
            data[tran_id]["workflow"] = self.workflow_id
        return data

    def build_review_json(self):
        file_path = os.path.join(
            settings.PROJECT_ROOT,
            "initials",
            "worksheet",
            "bk_itsm_builtin_other_workflow.json",
        )
        with open(file_path, "r", encoding="utf-8") as f:
            raw_data = f.read()

        raw_data = json.loads(raw_data)
        self.workflow_id += 1
        data = copy.deepcopy(raw_data)
        data = self.update_workflow_info(data)
        data["fields"], field_ids = self.update_fields_info(data["fields"])
        data["states"] = self.update_states_info(data["states"], field_ids)
        data["transitions"] = self.update_transition_info(data["transitions"])
        return data

    def build_export_json(self):
        file_path = os.path.join(
            settings.PROJECT_ROOT,
            "initials",
            "worksheet",
            "bk_itsm_builtin_other_workflow.json",
        )
        with open(file_path, "r", encoding="utf-8") as f:
            raw_data = f.read()

        raw_data = json.loads(raw_data)
        self.workflow_id += 1
        return raw_data

    def build_workflow_json(self):
        file_path = os.path.join(
            settings.PROJECT_ROOT,
            "initials",
            "worksheet",
            "bk_itsm_builtin_workflow.json",
        )
        with open(file_path, "r", encoding="utf-8") as f:
            raw_data = f.read()
        raw_data = json.loads(raw_data)
        self.workflow_id += 1
        data = copy.deepcopy(raw_data)
        data = self.update_workflow_info(data)
        data["fields"], field_ids = self.update_fields_info(data["fields"])
        data["states"] = self.update_states_info(data["states"], field_ids)
        data["transitions"] = self.update_transition_info(data["transitions"])
        return data


class ServiceInit(object):
    def __init__(self, worksheet_id, workflow_id, action, project_key):
        self.worksheet_id = worksheet_id
        self.workflow_id = workflow_id
        self.worksheet_handler = WorkSheetHandler(self.worksheet_id)
        self.worksheet = self.worksheet_handler.get_instance()
        self.action = action
        self.project_key = project_key

    def create_service(self):
        from itsm.service.models import Service

        service = Service.objects.create(**self.build_service_json())
        catalog_id = self.get_catalog_id(
            project_key=self.project_key, action_type=self.action
        )
        service.bind_catalog(catalog_id)

    def get_catalog_id(self, project_key, action_type):
        handler = ServiceCatalogHandler(
            project_key=project_key,
            operate_type=action_type,
        )
        catalog_id = handler.instance.id
        return catalog_id

    def build_service_json(self):
        action_map = {
            "ADD": "新增",
            "EDIT": "编辑",
            "DELETE": "删除",
            "DETAIL": "详情",
            "EXPORT": "导出",
        }

        data = {
            "can_ticket_agency": False,
            "desc": "",
            "display_type": "OPEN",
            "is_valid": True,
            "key": "change",
            "type": self.action,
            "name": "{}_{}".format(self.worksheet.name, action_map.get(self.action)),
            "owners": "admin",
            "project_key": self.project_key,
            "workflow_id": self.workflow_id,
            "worksheet_ids": [self.worksheet_id],
            "is_builtin": True,
        }
        return data


class WorksheetAutoInit(object):
    def __init__(self, worksheet_id, username, project_key):
        self.worksheet_id = worksheet_id
        self.username = (username,)
        self.project_key = project_key

    def update_first_state(self, workflow):
        first_state = workflow.first_state
        fields = first_state.fields
        for field_id in fields:
            field = Field.objects.get(id=field_id)
            field.state_id = first_state.id
            field.save()

    @transaction.atomic
    def __call__(self, *args, **kwargs):
        for action in (ADD_STATE, UPDATE_STATE, DELETE_STATE):
            workflow_json = WorkFlowInit(
                self.worksheet_id, action
            ).build_workflow_json()
            workflow = Workflow.objects.restore(workflow_json, self.username)[0]
            self.update_first_state(workflow)
            workflow_version = workflow.create_version()
            ServiceInit(
                self.worksheet_id, workflow_version.id, action, self.project_key
            ).create_service()
        for action in (DETAIL_STATE, EXPORT_STATE):
            workflow_json = WorkFlowInit(self.worksheet_id, action).build_review_json()
            workflow = Workflow.objects.restore(workflow_json, self.username)[0]
            self.update_first_state(workflow)
            workflow_version = workflow.create_version()
            ServiceInit(
                self.worksheet_id, workflow_version.id, action, self.project_key
            ).create_service()


class ServiceMigrate(object):
    def __init__(self, worksheet_id):
        """
        初始化对象内容
        """
        self.worksheet_id = worksheet_id
        self.worksheet_handler = WorkSheetHandler(self.worksheet_id)
        self.worksheet = self.worksheet_handler.get_instance()
        self.fields = WorkSheetFieldModelHandler().get_fields_by_worksheet(worksheet_id)

    def diff_fields(self):
        """
        生成变更列表
        """
        workflow_fields = set([field.key for field in self.workflow.fields.all()])
        worksheet_fields_list = []
        for field_id in self.worksheet.fields:
            field = self.fields.get(id=field_id)
            # 过滤计算控件和自动编号
            if ignore_fields_type(field.type):
                continue
            key = "{}_{}".format(self.worksheet.key, field.key)
            worksheet_fields_list.append(key)

        worksheet_fields = set(worksheet_fields_list)
        # 默认的 title 字段
        # worksheet_fields.add("title")
        # 为更新生成 id 字段
        if self.action == UPDATE_STATE:
            worksheet_fields_list.insert(0, "id")
            worksheet_fields.add("id")
        # 获取需要添加的字段
        add_fields = worksheet_fields.difference(workflow_fields)
        # 获取被移除的字段
        drop_fields = workflow_fields.difference(worksheet_fields)
        # 获取需要更新的字段
        update_fields = worksheet_fields.intersection(worksheet_fields)

        return add_fields, drop_fields, update_fields, worksheet_fields_list

    def add_fields(self, add_fields):
        """
        为 workflow 增加字段
        """
        fields = []
        for field in self.fields:
            # 字段新增进行迁移时，跳过计算控件
            if ignore_fields_type(field.type):
                continue
            key = "{}_{}".format(self.worksheet.key, field.key)
            field_meta = field.meta
            if isinstance(field.meta, str):
                field_meta = json.loads(field_meta)
            meta = copy.deepcopy(field_meta)
            meta.update(
                {
                    "worksheet": {
                        "id": self.worksheet.id,
                        "key": self.worksheet.key,
                        "field_key": field.key,
                    }
                }
            )
            if key in add_fields:
                fields.append(
                    Field(
                        type=field.type,
                        key=key,
                        name=field.name,
                        layout="COL_12",
                        source="CUSTOM",
                        validate_type=field.validate_type,
                        workflow_id=self.workflow.id,
                        state_id=self.workflow.first_state.id,
                        choice=field.choice,
                        source_type=field.source_type,
                        api_instance_id=field.api_instance_id,
                        kv_relation=field.kv_relation,
                        default=field.default,
                        meta=meta,
                        regex=field.regex,
                        tips=field.tips,
                    )
                )
        Field.objects.bulk_create(fields)

    def update_fields(self, update_fields):

        for field in self.fields:
            key = "{}_{}".format(self.worksheet.key, field.key)
            meta = copy.deepcopy(field.meta)
            meta.update(
                {
                    "worksheet": {
                        "id": self.worksheet.id,
                        "key": self.worksheet.key,
                        "field_key": field.key,
                    }
                }
            )
            if key in update_fields:
                workflow_filed = Field.objects.filter(
                    state_id=self.workflow.first_state.id, key=key
                ).first()
                if workflow_filed is not None:
                    # 字段更新进行迁移时，跳过无需迁移控件
                    if ignore_fields_type(field.type):
                        continue
                    workflow_filed.type = field.type
                    workflow_filed.name = field.name
                    workflow_filed.layout = field.layout
                    workflow_filed.validate_type = field.validate_type
                    workflow_filed.choice = field.choice
                    workflow_filed.source_type = field.source_type
                    workflow_filed.api_instance_id = field.api_instance_id
                    workflow_filed.kv_relation = field.kv_relation
                    workflow_filed.default = field.default
                    workflow_filed.regex = field.regex
                    workflow_filed.meta = meta
                    workflow_filed.tips = field.tips
                    workflow_filed.num_range = field.num_range
                    workflow_filed.save()

    def drop_fields(self, drop_fields):
        """
        为 workflow 删除字段
        """
        Field.objects.filter(key__in=drop_fields, workflow=self.workflow).delete()

    def build_mapping(self):
        """
        构造字段映射
        """
        mapping = []
        for field in self.fields:
            mapping.append(
                {
                    "key": field.key,
                    "type": VALUE_FROM_FIELD,
                    "value": "${param_%s_%s}" % (self.worksheet.key, field.key),
                }
            )
        return mapping

    def update_start_state(self, fields):
        """
        更新提单节点字段
        """
        fields_obj = Field.objects.filter(workflow=self.workflow, key__in=fields)
        sort_fields_id = [fields_obj.get(key=field_key).id for field_key in fields]
        start_state = self.workflow.states.get(type=NORMAL_STATE)
        start_state.fields = sort_fields_id
        start_state.save()

    def update_data_proc_state(self):
        """
        更新数据处理节点 extras 字段映射信息
        """
        if self.action in (ADD_STATE, UPDATE_STATE):
            data_proc_state = self.workflow.states.get(type=DATA_PROC_STATE)
            data_proc_state.extras["dataManager"]["mapping"] = self.build_mapping()
            data_proc_state.save()

    def migrate_service_name(self, new_name):
        for action in (
            ADD_STATE,
            UPDATE_STATE,
            DETAIL_STATE,
            EXPORT_STATE,
            DELETE_STATE,
        ):
            # 获取 workflow
            action_map = {
                "ADD": "新增",
                "EDIT": "编辑",
                "DELETE": "删除",
                "DETAIL": "详情",
                "EXPORT": "导出",
            }

            service_name = "{}_{}".format(self.worksheet.name, action_map.get(action))

            try:
                service = Service.objects.get(
                    name=service_name,
                    project_key=self.worksheet.project_key,
                    is_builtin=True,
                )
            except Service.DoesNotExist:
                if action == UPDATE_STATE:
                    service_name = "{}_{}".format(self.worksheet.name, "更新")
                    service = Service.objects.get(
                        name=service_name,
                        project_key=self.worksheet.project_key,
                        is_builtin=True,
                    )

            new_service_name = "{}_{}".format(new_name, action_map.get(action))

            service.name = new_service_name
            service.save()

    @transaction.atomic
    def __call__(self, *args, **kwargs):
        for action in (ADD_STATE, UPDATE_STATE, DETAIL_STATE):
            self.action = action

            # 获取 workflow
            action_map = {"ADD": "新增", "EDIT": "编辑", "DELETE": "删除", "DETAIL": "详情"}
            service_name = "{}_{}".format(
                self.worksheet.name, action_map.get(self.action)
            )

            try:
                service = Service.objects.get(
                    name=service_name, project_key=self.worksheet.project_key
                )
            except Service.DoesNotExist:
                if self.action == UPDATE_STATE:
                    service_name = "{}_{}".format(self.worksheet.name, "更新")
                    service = Service.objects.get(
                        name=service_name, project_key=self.worksheet.project_key
                    )

            self.workflow = Workflow.objects.get(id=service.workflow.workflow_id)
            # 更新内容
            add_fields, drop_fields, update_fields, all_fields = self.diff_fields()
            self.add_fields(add_fields)
            self.drop_fields(drop_fields)
            self.update_fields(update_fields)
            self.update_start_state(all_fields)
            if action in [ADD_STATE, UPDATE_STATE]:
                self.update_data_proc_state()


class ServiceManager:
    def __init__(self, worksheet):
        self.worksheet = worksheet

    @transaction.atomic
    def delete_service(self):
        """
        删除服务
        """
        for action in (
            ADD_STATE,
            UPDATE_STATE,
            DELETE_STATE,
            DETAIL_STATE,
            EXPORT_STATE,
        ):
            action_map = {
                "ADD": "新增",
                "EDIT": "编辑",
                "DELETE": "删除",
                "DETAIL": "详情",
                "EXPORT": "导出",
            }
            service_name = "{}_{}".format(self.worksheet.name, action_map.get(action))
            try:
                service = Service.objects.get(
                    name=service_name, project_key=self.worksheet.project_key
                )
            except Service.DoesNotExist:
                if action == UPDATE_STATE:
                    service_name = "{}_{}".format(self.worksheet.name, "更新")
                    service = Service.objects.get(
                        name=service_name, project_key=self.worksheet.project_key
                    )
            CatalogService.objects.filter(
                catalog_id=service.catalog_id,
                service_id=service.id,
            ).delete()

            try:
                workflow = Workflow.objects.get(id=service.workflow.workflow_id)
                workflow.delete()
            except Exception:
                pass

            service.delete()
