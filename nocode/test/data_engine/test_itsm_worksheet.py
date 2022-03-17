# -*- coding: utf-8 -*-
import copy
from django.db import connection
from django.test import TestCase, override_settings
from blueapps.core.celery.celery import app

from itsm.component.constants import OPERATE_CATALOG
from itsm.pipeline_plugins.components.collections.itsm_worksheet import (
    DataProcessingService,
)
from itsm.project.handler.project_handler import ProjectHandler
from itsm.project.models import ProjectConfig, Project
from itsm.service.models import Service
from itsm.service.validators import service_validate
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
from nocode.worksheet.models import WorkSheet
from pipeline.core.data.base import DataObject


class PipelineTest(TestCase):
    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def setUp(self):
        app.conf.update(CELERY_ALWAYS_EAGER=True)
        Project.objects.all().delete()
        ProjectConfig.objects.all().delete()
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
        instance = self.fields_batch_save(instance)
        ServiceMigrate(instance.id)()
        self.project_publish()
        return instance

    def fields_batch_save(self, worksheet):
        data = {
            "worksheet_id": worksheet.id,
            "fields": [
                {
                    "type": "INT",
                    "name": "数字1",
                    "desc": "",
                    "regex": "EMPTY",
                    "layout": "COL_12",
                    "unique": False,
                    "validate_type": "OPTION",
                    "source_type": "CUSTOM",
                    "api_instance_id": None,
                    "kv_relation": {},
                    "default": 0,
                    "choice": [],
                    "worksheet_id": worksheet.id,
                    "meta": {},
                    "num_range": [],
                },
                {
                    "type": "INT",
                    "name": "数字2",
                    "desc": "",
                    "regex": "EMPTY",
                    "layout": "COL_12",
                    "unique": False,
                    "validate_type": "OPTION",
                    "source_type": "CUSTOM",
                    "api_instance_id": None,
                    "kv_relation": {},
                    "default": 0,
                    "choice": [],
                    "worksheet_id": worksheet.id,
                    "meta": {},
                    "num_range": [],
                },
            ],
        }

        url = "/api/worksheet/fields/batch_save/"
        rsp = self.client.post(
            path=url,
            data=data,
            content_type="application/json",
        )
        self.assertEqual(rsp.data["code"], "OK")
        self.assertEqual(len(rsp.data["data"]), 2)
        return WorkSheet.objects.get(id=worksheet.id)

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

    def data_process_state(self, service):
        for state in service.workflow.states.values():
            if state["type"] == "DATA-PROC":
                data_process_state = state["id"]
                break
        return data_process_state

    def test_add_operate(self):
        service = Service.objects.get(
            project_key=CREATE_PROJECT_DATA["key"], name="test_新增"
        )
        ticket_id = self.create_ticket(service)
        data_process_state = self.data_process_state(service)
        excute_data = DataObject(
            inputs={"state_id": data_process_state, "_loop": 0}, outputs={"_loop": 0}
        )
        excute_parent_data = DataObject(
            inputs={"ticket_id": ticket_id}, outputs={"is_first_execute": False}
        )

        auto_service = DataProcessingService(name="itsm")
        auto_service._runtime_attrs = {"by_flow": 1}
        result = auto_service.execute(excute_data, excute_parent_data)
        self.assertEqual(result, True)
        queryset = self.manager.get_queryset()
        self.assertEqual(len(queryset), 1)
