# -*- coding: utf-8 -*-

import copy
import json
import os
from datetime import datetime

from django.db import connection
from django.test import TestCase, override_settings
from django.conf import settings

from blueapps.core.celery.celery import app

from itsm.component.constants import OPERATE_CATALOG, UPDATE_STATE, DELETE_STATE
from itsm.pipeline_plugins.components.collections.itsm_worksheet_query import (
    DataQueryService,
)

from itsm.project.handler.project_handler import ProjectHandler
from itsm.project.models import ProjectConfig, Project
from itsm.service.models import Service
from itsm.service.validators import service_validate
from itsm.workflow.models import State, GlobalVariable, Workflow
from nocode.data_engine.core.managers import DataManager
from nocode.project_manager.handlers.module_handler import (
    ProjectModuleHandler,
    ServiceModuleHandler,
)
from nocode.project_manager.handlers.project_version_handler import (
    WorksheetIndexHandler,
    WorkSheetMigrateHandler,
    ProjectVersionModelHandler,
)
from nocode.project_manager.handlers.publish_log_handler import PublishLogModelHandler
from nocode.test.data_engine.params import CREATE_PROJECT_DATA, WORKSHEET_DATA
from nocode.utils.worksheet_tool import ServiceMigrate
from nocode.worksheet.handlers.moudule_handler import ServiceHandler, DjangoHandler
from nocode.worksheet.models import WorkSheet, WorkSheetField
from pipeline.core.data.base import DataObject


class CreateQueryService:
    def __init__(self, worksheet, action, worksheet_fields):
        self.worksheet = worksheet
        self.action = action
        self.worksheet = worksheet
        self.workflow_id = 0
        self.worksheet_fields = worksheet_fields

    def build_extras(self):
        """
        构造 extras 字段
        """
        extras = {
            "worksheet_id": self.worksheet.id,
            "field_list": self.worksheet_fields,
        }
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

    def create_global_field(self, workflow_id, state):
        GlobalVariable.objects.get_or_create(
            key=f"data_query_result_{state.id}",
            name="数据是否存在",
            type="STRING",
            is_valid=True,
            state_id=state.id,
            flow_id=workflow_id,
        )

        from itsm.workflow.handler.worksheet_fields_handler import (
            WorkSheetFieldModelHandler,
        )

        extra = self.build_extras()
        WorkSheetFieldModelHandler().create_global_field_from_worksheet(
            worksheet_field_ids=extra["field_list"],
            state=state,
        )

    def create_query_workflow(self):
        workflow_json = self.build_review_json()
        workflow = Workflow.objects.restore(workflow_json, "tester")[0]
        return workflow

    def build_review_json(self):
        file_path = os.path.join(
            settings.PROJECT_ROOT,
            "nocode",
            "test",
            "worksheet",
            "query_state_workflow.json",
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

    def get_catalog_id(self, project_key, action_type):
        from itsm.service.handler.service_handler import ServiceCatalogHandler

        handler = ServiceCatalogHandler(
            project_key=project_key,
            operate_type=action_type,
        )
        catalog_id = handler.instance.id
        return catalog_id

    def import_fields_data_source_state(self, service):
        from itsm.workflow.handler.worksheet_fields_handler import (
            WorkSheetFieldModelHandler,
        )

        state = State.objects.get(id=service.first_state_id)
        WorkSheetFieldModelHandler().copy_fields_from_worksheet_field(
            worksheet_field_ids=self.worksheet_fields, service=service, state=state
        )

    def create_service(self):
        workflow_instance = self.create_query_workflow()
        version = workflow_instance.create_version()
        from itsm.service.models import Service

        data = {
            "can_ticket_agency": False,
            "desc": "",
            "display_type": "OPEN",
            "is_valid": True,
            "key": "change",
            "type": "ADD",
            "name": "test_query",
            "owners": "admin",
            "project_key": CREATE_PROJECT_DATA["key"],
            "workflow_id": version.id,
            "worksheet_ids": [self.worksheet.id],
            "is_builtin": True,
        }
        service = Service.objects.create(**data)
        catalog_id = self.get_catalog_id(
            project_key=CREATE_PROJECT_DATA["key"], action_type="ADD"
        )
        service.bind_catalog(catalog_id)
        state = State.objects.get(workflow_id=workflow_instance.id, type="DATA-QUERY")
        self.create_global_field(workflow_instance.id, state)
        self.import_fields_data_source_state(service=service)
        return service


class PipelineTest(TestCase):
    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def setUp(self):
        app.conf.update(CELERY_ALWAYS_EAGER=True)
        Project.objects.all().delete()
        ProjectConfig.objects.all().delete()
        Service.objects.all().delete()

        project = Project.objects.create(**CREATE_PROJECT_DATA)
        project_config = {
            "workflow_prefix": "test",
            "project_key": CREATE_PROJECT_DATA["key"],
        }
        ProjectConfig.objects.create(**project_config)
        ProjectHandler(instance=project).init_operate_catalogs(OPERATE_CATALOG)
        self.worksheet = self.create_worksheet()
        with connection.schema_editor() as schema_editor:
            in_atomic_block = schema_editor.connection.in_atomic_block
            schema_editor.connection.in_atomic_block = False
            db_name = "{0}_{1}".format(
                WORKSHEET_DATA["project_key"], WORKSHEET_DATA["key"]
            )
            DjangoHandler(db_name).init_db()
            schema_editor.connection.in_atomic_block = in_atomic_block
        self.manager = DataManager(self.worksheet.id)
        service = Service.objects.get(
            project_key=CREATE_PROJECT_DATA["key"], name="test_新增"
        )
        self.create_ticket(service)

    def create_worksheet(self):
        instance = WorkSheet.objects.create(**WORKSHEET_DATA)
        ServiceHandler(instance).init_service()
        self.fields_batch_save(instance)
        ServiceMigrate(instance.id)()
        self.project_publish()
        return instance

    def fields_batch_save(self, instance):
        fields = [
            {
                "meta": {},
                "choice": [],
                "kv_relation": {},
                "key": "shu_zi_1",
                "name": "数字1",
                "desc": "",
                "type": "INT",
                "layout": "COL_12",
                "validate_type": "OPTION",
                "source_type": "CUSTOM",
                "api_instance_id": 0,
                "default": "0",
                "worksheet_id": instance.id,
                "regex": "EMPTY",
            },
            {
                "meta": {},
                "choice": [],
                "kv_relation": {},
                "create_at": "2022-01-27 15:37:28",
                "key": "shu_zi_2",
                "name": "数字2",
                "desc": "",
                "type": "INT",
                "layout": "COL_12",
                "validate_type": "OPTION",
                "source_type": "CUSTOM",
                "api_instance_id": 0,
                "default": "0",
                "worksheet_id": instance.id,
                "regex": "EMPTY",
            },
        ]
        field_ids = []
        for item in fields:
            field = WorkSheetField.objects.create(**item)
            field_ids.append(field.id)
        instance.fields = field_ids
        instance.save()
        ServiceMigrate(instance.id)()

    def project_publish(self):
        handler = PublishLogModelHandler(task_id=1)
        project_module_handler = ProjectModuleHandler(
            project_key=CREATE_PROJECT_DATA["key"]
        )
        # 变更应用状态为发布中
        project_module_handler.updating()
        # 更新所有字段详情信息
        WorksheetIndexHandler(
            CREATE_PROJECT_DATA["key"], handler
        ).migrate_worksheet_fields()
        # 删除被删除的工作表:
        WorkSheetMigrateHandler(
            project_key=CREATE_PROJECT_DATA["key"], log_handler=handler
        ).migrate_worksheet()
        # 生成一个新的版本
        version = ProjectVersionModelHandler(
            project_key=CREATE_PROJECT_DATA["key"], log_handler=handler
        ).create_version()
        # 更新版本号
        project_module_handler.update_version(version.version_number)
        # 更新所有服务
        ServiceModuleHandler(project_key=CREATE_PROJECT_DATA["key"]).update_service()

        return version.version_number

    def create_ticket(self, service, action="add", row_id=None):
        # 获取对应的流程版本
        service, catalog_services = service_validate(service.id)
        field_ids = service.workflow.first_state["fields"]

        fields = []
        if action in ["add", "edit"]:
            for field_id in field_ids:
                version_field = service.workflow.get_field(field_id)
                # 忽略错误的id
                if version_field is None:
                    continue

                field = copy.deepcopy(version_field)
                if action == "edit" and field["key"] == "id":
                    ticket_data = {
                        "choice": [],
                        "id": field["id"],
                        "key": "id",
                        "type": "INT",
                        "value": row_id,
                    }
                elif action == "del":
                    ticket_data = {
                        "choice": [],
                        "id": field["id"],
                        "key": field["key"],
                        "type": field["type"],
                        "value": row_id,
                    }
                    fields.append(ticket_data)
                    break
                else:
                    ticket_data = {
                        "choice": [],
                        "id": field["id"],
                        "key": field["key"],
                        "type": field["type"],
                        "value": "1",
                    }

                fields.append(ticket_data)

        url = "/api/ticket/receipts/create_ticket/"
        create_ticket_params = {
            "service_id": service.id,
            "fields": fields,
            "creator": "admin",
        }
        rsp = self.client.post(
            path=url,
            data=create_ticket_params,
            content_type="application/json",
        )
        self.assertEqual(rsp.data["code"], "OK")
        self.assertEqual(rsp.data["message"], "success")
        ticket_id = rsp.data["data"]["id"]
        return ticket_id

    def data_query_state(self, service):
        for state in service.workflow.states.values():
            if state["type"] == "DATA-QUERY":
                data_process_state = state["id"]
                return data_process_state

    def test_query_operate(self):
        service = Service.objects.get(
            project_key=CREATE_PROJECT_DATA["key"], name="test_新增"
        )
        self.create_ticket(service)
        queryset = self.manager.get_queryset()
        self.assertEqual(len(queryset), 2)

        service_query = CreateQueryService(
            worksheet=self.worksheet,
            action="ADD",
            worksheet_fields=self.worksheet.fields,
        ).create_service()

        self.project_publish()
        ticket_id = self.create_ticket(service_query)

        data_query_state = self.data_query_state(service_query)
        excute_data = DataObject(
            inputs={"state_id": data_query_state, "_loop": 0}, outputs={"_loop": 0}
        )
        excute_parent_data = DataObject(
            inputs={"ticket_id": ticket_id}, outputs={"is_first_execute": False}
        )

        auto_service = DataQueryService(name="itsm")
        auto_service._runtime_attrs = {"by_flow": 1}
        result = auto_service.execute(excute_data, excute_parent_data)
        self.assertEqual(result, True)
