# -*- coding: utf-8 -*-
import copy
import json

from blueapps.core.celery.celery import app
from django.db import connection

from django.test import TestCase, override_settings

from itsm.component.constants import OPERATE_CATALOG
from itsm.project.handler.project_handler import ProjectHandler
from itsm.project.models import Project, ProjectConfig
from itsm.service.models import Service
from nocode.data_engine.core.managers import DataManager
from nocode.page.handlers.page_handler import PageModelHandler
from nocode.page.models import Page
from nocode.test.data_engine.params import (
    CREATE_PROJECT_DATA,
    SON_POINT,
    WORKSHEET_DATA,
)
from nocode.utils.worksheet_tool import ServiceMigrate
from nocode.worksheet.handlers.moudule_handler import ServiceHandler, DjangoHandler
from nocode.worksheet.models import WorkSheet, WorkSheetField


class TicketDataEngine(TestCase):
    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def setUp(self):
        app.conf.update(CELERY_ALWAYS_EAGER=True)
        Project.objects.all().delete()
        ProjectConfig.objects.all().delete()
        project = Project.objects.create(**CREATE_PROJECT_DATA)
        ProjectHandler(instance=project).init_operate_catalogs(OPERATE_CATALOG)
        project_config = {
            "workflow_prefix": "test",
            "project_key": CREATE_PROJECT_DATA["key"],
        }
        ProjectConfig.objects.create(**project_config)
        PageModelHandler().create_root(project_key=project.key)
        self.worksheet = self.create_worksheet()
        self.page = self.page_batch_save()
        self.field_batch_save()
        self.project_publish()
        self.service = Service.objects.get(
            project_key=CREATE_PROJECT_DATA["key"], name="test_新增"
        )
        self.version_number = Project.objects.get(
            key=CREATE_PROJECT_DATA["key"]
        ).version_number

    def create_worksheet(self):
        worksheet = WorkSheet.objects.create(**WORKSHEET_DATA)

        with connection.schema_editor() as schema_editor:
            in_atomic_block = schema_editor.connection.in_atomic_block
            schema_editor.connection.in_atomic_block = False
            db_name = "{0}_{1}".format(
                WORKSHEET_DATA["project_key"], WORKSHEET_DATA["key"]
            )
            DjangoHandler(db_name).init_db()
            schema_editor.connection.in_atomic_block = in_atomic_block

        ServiceHandler(worksheet).init_service()

        return worksheet

    def field_batch_save(self):
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
                "worksheet_id": self.worksheet.id,
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
                "worksheet_id": self.worksheet.id,
                "regex": "EMPTY",
            },
        ]
        field_ids = []
        for item in fields:
            field = WorkSheetField.objects.create(**item)
            field_ids.append(field.id)
        self.worksheet.fields = field_ids
        self.worksheet.save()
        ServiceMigrate(self.worksheet.id)()

    def project_publish(self):
        publish_rep = self.client.post(
            path="/api/project/manager/publish/",
            data=json.dumps({"project_key": CREATE_PROJECT_DATA["key"]}),
            content_type="application/json",
        )
        self.assertEqual(publish_rep.data["code"], "OK")
        self.assertEqual(publish_rep.data["message"], "success")

    def set_first_state_field(self):
        field_ids = self.service.workflow.first_state["fields"]
        fields = []
        for field_id in field_ids:
            version_field = self.service.workflow.get_field(field_id)
            # 忽略错误的id
            if version_field is None:
                continue

            field = copy.deepcopy(version_field)
            set_field = {
                "choice": field.get("choice"),
                "id": field.get("id"),
                "key": field.get("key"),
                "type": field.get("type"),
                "value": "1",
            }
            fields.append(set_field)
        return fields

    def create_ticket(self):
        url = "/api/ticket/receipts/create_ticket/"
        create_ticket_params = {
            "service_id": self.service.id,
            "fields": self.set_first_state_field(),
            "creator": "admin",
        }
        rsp = self.client.post(
            path=url,
            data=json.dumps(create_ticket_params),
            content_type="application/json",
        )
        self.assertEqual(rsp.data["code"], "OK")
        self.assertEqual(rsp.data["message"], "success")
        ticket_id = rsp.data["data"]["id"]
        return ticket_id

    def page_batch_save(self):
        root = Page.objects.get(key="root", project_key=CREATE_PROJECT_DATA["key"])
        for point in SON_POINT:
            point.setdefault("parent_id", root.id)
            resp = self.client.post("/api/page_design/page/", point)
            self.assertEqual(resp.data["result"], True)

        page = Page.objects.get(name="page2", type="LIST")

        data = {
            "page_id": page.id,
            "components": [
                {
                    "page_id": page.id,
                    "value": self.worksheet.id,
                    "type": "LIST",
                    "config": {
                        "buttonGroup": [],
                        "fields": [self.worksheet.fields],
                        "optionList": [],
                        "searchInfo": [],
                        "sys_fields": [],
                        "show_mode": {"mode": 0},
                        "time_range": "all",
                    },
                }
            ],
        }

        res = self.client.post(
            "/api/page_design/page_component/batch_save/",
            data,
            content_type="application/json",
        )
        self.assertEqual(res.data["result"], True)
        self.assertEqual(res.data["message"], "success")
        self.assertEqual(len(res.data["data"]), 1)
        return page

    def data_process_state(self, service):
        for state in service.workflow.states.values():
            if state["type"] == "DATA-PROC":
                data_process_state = state["id"]
                break
        return data_process_state

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_list_component_data(self):
        page = Page.objects.get(name="page2", type="LIST")

        for i in range(3):
            self.create_ticket()
        manage = DataManager(self.worksheet.id)
        queryset = manage.get_queryset()
        self.assertEqual(len(queryset), 3)

        url = "/api/engine/data/list_component_data/"
        list_data = {"page_id": page.id, "version_number": self.version_number}
        res = self.client.post(
            url,
            list_data,
            content_type="application/json",
        )

        self.assertEqual(res.data["code"], "OK")
        self.assertEqual(len(res.data["data"]["items"]), 3)
