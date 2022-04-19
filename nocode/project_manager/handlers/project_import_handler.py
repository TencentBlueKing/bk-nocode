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
import random
import string

from common.log import logger
from itsm.service.handler.service_handler import ServiceCatalogHandler
from itsm.service.models import Service
from itsm.workflow.models import Workflow
from nocode.base.basic import get_random_key
from nocode.page.models import Page, PageComponent
from nocode.project_manager.exceptions import (
    ProjectInitError,
    WorkSheetInitError,
    WorkSheetFieldInitError,
)
from nocode.worksheet.handlers.moudule_handler import DjangoHandler
from nocode.worksheet.models import WorkSheet, WorkSheetField


class ProjectImportHandler:
    def __init__(self, data, request):
        self.request = request
        self.data = data
        self.filed_map = {}
        self.worksheet_map = {}
        self.service_map = {}
        self.project_key = None
        self.page_map = {}

    def generate_project_key(self):
        num = string.ascii_letters
        return "".join(random.sample(num, 10))

    def create_project(self, project_serializer):
        project_data = project_serializer.validated_data
        project_data["creator"] = self.request.user.username
        self.project_key = project_data["key"]
        try:
            logger.info("正在导入应用")
            project_serializer.save()
        except Exception as e:
            logger.exception("应用初始化失败: {}, {}".format(project_data["key"], e))
            raise ProjectInitError()

    def create_worksheet(self, worksheets):
        try:
            logger.info("正在初始化工作表")
            for worksheet in worksheets:
                old_id = worksheet.pop("id")
                worksheet["project_key"] = self.project_key
                ws = WorkSheet.objects.create(**worksheet)
                self.worksheet_map[old_id] = ws.id
                db_name = "{0}_{1}".format(self.project_key, ws.key)
                logger.info("正在准备初始化db表, db_name={}".format(db_name))
                DjangoHandler(db_name).init_db()
        except Exception as e:
            logger.exception("表单初始化失败,error: {}".format(e))
            raise WorkSheetInitError()

    def create_worksheet_filed(self, worksheet_field):
        try:
            logger.info("正在初始化工作表字段")
            for fields in worksheet_field.values():
                for field in fields:
                    old_id = field.pop("id")
                    field["worksheet_id"] = self.worksheet_map[field["worksheet_id"]]
                    field.pop("api_info", None)
                    field = WorkSheetField.objects.create(**field)
                    self.filed_map[old_id] = field.id
        except Exception as e:
            logger.exception("工作表字段失败, error:{}".format(e))
            import traceback

            traceback.print_exc()
            raise WorkSheetFieldInitError(e)

    def init_tree(self, node, parent_id=None):
        old_id = node["id"]
        if parent_id is None:
            node_id = Page.objects.get(project_key=self.project_key, key="root").id
        else:
            node_id = Page.objects.create(
                key=get_random_key(node["name"]),
                order=node["order"],
                project_key=self.project_key,
                parent_id=parent_id,
                type=node["type"],
                name=node["name"],
            ).id

        self.page_map[old_id] = node_id
        for item in node.get("children", []):
            self.init_tree(item, node_id)

    def create_page(self, page):
        """
        初始化一棵树
        """
        logger.info("正在初始化page tree")
        self.init_tree(page[0], None)

    def create_page_components(self, page_components):
        logger.info("正在初始化页面组件")
        for key, value in page_components.items():
            new_page_id = self.page_map.get(int(key))
            value["page_id"] = new_page_id
            value.pop("id")
            PageComponent.objects.create(**value)

    def create_service(self, services):
        logger.info("正在初始化服务")
        for service in services:
            service["project_key"] = self.project_key
            old_service_id = service.pop("id")
            worksheet_ids = service["worksheet_ids"]
            new_worksheet_ids = []
            for worksheet_id in worksheet_ids:
                new_worksheet_ids.append(self.worksheet_map[worksheet_id])

            service["worksheet_ids"] = new_worksheet_ids

            states = service["workflow"]["states"]
            for state in states.values():
                if state["type"] == "DATA-PROC":
                    old_worksheet_id = state["extras"]["dataManager"]["worksheet_id"]
                    state["extras"]["dataManager"]["worksheet_id"] = self.worksheet_map[
                        old_worksheet_id
                    ]

            workflow_tag_data = service.pop("workflow")
            workflow = Workflow.objects.restore(workflow_tag_data, "system")[0]
            version = workflow.create_version()
            service["workflow_id"] = version.id
            new_service_id = Service.objects.create(**service).id
            self.service_map[old_service_id] = new_service_id

    def migrate_page_components(self):
        logger.info("正在迁移页面组件，修改所有的field_id 和 功能")
        page_components = PageComponent.objects.filter(
            page_id__in=self.page_map.values()
        )
        for page_component in page_components:
            if page_component.type in ["FUNCTION", "SHEET"]:
                page_component.value = self.service_map[int(page_component.value)]
            if page_component.type == "LIST":
                page_component.value = self.worksheet_map[int(page_component.value)]
                for button in page_component.config.get("buttonGroup", []):
                    button["value"] = self.service_map[int(button["value"])]

                new_fields = []
                for filed in page_component.config.get("fields", []):
                    new_fields.append(self.filed_map[filed])

                page_component.config["fields"] = new_fields

                new_search_fields = []
                for search_filed in page_component.config.get("searchInfo", []):
                    new_search_fields.append(self.filed_map[search_filed])

                page_component.config["searchInfo"] = new_search_fields

            page_component.save()

    def get_catalog_id(self, project_key, action_type):
        handler = ServiceCatalogHandler(
            project_key=project_key,
            operate_type=action_type,
        )
        catalog_id = handler.instance.id
        return catalog_id

    def bind_service_catalogs(self):
        logger.info("正在初始化服务配置，将所有的服务绑定到服务目录")
        services = Service.objects.filter(project_key=self.project_key)
        for service in services:
            catalog_id = self.get_catalog_id(
                project_key=self.project_key, action_type=service.type
            )
            service.bind_catalog(catalog_id)

    def import_project(self, project_serializer):
        worksheet = self.data.get("worksheet")
        worksheet_field = self.data.get("worksheet_field")
        page = self.data.get("page")
        page_component = self.data.get("page_component")
        service = self.data.get("service")

        self.create_project(project_serializer)
        logger.info("初始化应用成功")

        self.create_worksheet(worksheet)
        self.create_worksheet_filed(worksheet_field)
        logger.info("初始化表单成功")

        self.create_page(page)
        self.create_page_components(page_component)
        logger.info("初始化页面成功")

        self.create_service(service)
        self.bind_service_catalogs()
        logger.info("初始化功能成功")

        self.migrate_page_components()
        logger.info("初始化迁移页面组件成功")
