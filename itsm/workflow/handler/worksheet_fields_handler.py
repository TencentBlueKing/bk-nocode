# -*- coding: utf-8 -*-
import json
import random
import string
import uuid

from common.log import logger
from itsm.workflow.models import Field, GlobalVariable

from itsm.workflow.signals.handlers import state_change_project_change
from nocode.base.basic import ignore_fields_type
from nocode.worksheet.exceptions import WorkSheetFieldDoesNotExist
from nocode.worksheet.handlers.worksheet_field_handler import WorkSheetFieldModelHandler
from nocode.worksheet.handlers.worksheet_handler import WorkSheetModelHandler


class WorkSheetFieldModelHandler(WorkSheetFieldModelHandler):
    def retrieve(self, worksheet_field_id):
        return self.filter(pk=worksheet_field_id).first()

    def import_fields_repeat_check(self, field, field_key):
        # 重复导入规避
        # 同一节点内重复导入
        if field["meta"].get("worksheet"):
            if field["meta"]["worksheet"]["field_key"] == field_key:
                return True

    def _create_fields_struct(self, worksheet_field_ids):
        """
        构建字段信息数据结构
        """
        # 获取filed信息
        if isinstance(worksheet_field_ids, list):
            fields = [
                self.all_worksheet_field.get(pk=worksheet_field_id)
                for worksheet_field_id in worksheet_field_ids
            ]
        else:
            fields = self.retrieve(worksheet_field_ids)
        # 数据构造
        """
        {
            "worksheet_id":{
                "key": "worksheet_key",
                "items": [
                    worksheetfields.tag_data(),
                    ....
                ] 
            },
            ...
        }
        """
        if not fields:
            raise WorkSheetFieldDoesNotExist("没有工作表字段")
        data_struct = {}
        for item in fields:
            # 同一表单下，不同字段增加
            if item.worksheet_id in data_struct.keys():
                data_struct[item.worksheet_id]["items"].append(item.tag_data())
            else:
                # 不同表单下，字段段增加
                data_struct[item.worksheet_id] = {}
                item_data = item.tag_data()
                data_struct[item.worksheet_id]["items"] = []
                data_struct[item.worksheet_id]["items"].append(item_data)

                worksheet = WorkSheetModelHandler(
                    worksheet_id=item.worksheet_id
                ).instance
                data_struct[item.worksheet_id]["key"] = worksheet.key
                data_struct[item.worksheet_id]["name"] = worksheet.name
        return data_struct

    def _create_workflow_fields(self, data_struct, state, service):
        """
        流程内导入表单字段
        """
        field_ids = []
        logger.info("创建新增字段id列表：{field_ids}".format(field_ids=field_ids))
        for data in data_struct.values():
            for item in data["items"]:
                item.pop("id")
                item.pop("unique")
                item.pop("api_info")
                # 字段更新进行迁移时，跳过无需迁移控件
                if ignore_fields_type(item["type"]):
                    continue
                worksheet_id = item.pop("worksheet_id")
                worksheet_key = data["key"]
                worksheet_name = data["name"]
                field_key = item.pop("key")
                key = uuid.uuid3(uuid.uuid1(), uuid.uuid4().hex).hex
                if key[0].isdigit():
                    # 开头为数字，重新生成
                    first_letter = random.choice(string.ascii_letters)
                    key = first_letter + key[1:]
                item["key"] = key
                item["state_id"] = state.id
                item["workflow_id"] = service.workflow.workflow_id

                if isinstance(item["meta"], str):
                    item["meta"] = json.loads(item["meta"])
                item["meta"].update(
                    {
                        "worksheet": {
                            "id": worksheet_id,
                            "key": worksheet_key,
                            "name": worksheet_name,
                            "field_key": field_key,
                        },
                    }
                )
                # 重复导入规避
                # 同一节点内重复导入
                fields_object = Field.objects.filter(
                    state=item["state_id"], is_deleted=False
                ).values("id", "meta")

                exist_flag = None
                for field in fields_object:
                    exist_flag = self.import_fields_repeat_check(field, field_key)
                    if exist_flag:
                        break
                if exist_flag:
                    continue

                else:
                    # 默认值联动规则中有不可修改选项
                    if item["meta"].get("data_config"):
                        if not item["meta"]["data_config"].get("changeFields", True):
                            item["is_readonly"] = True
                    field = Field.objects.create(**item)
                    logger.info("新增流程字段id：{field}".format(field=field.id))
                    field_ids.append(field.id)

        return field_ids

    def _create_global_field(self, data_struct, state):
        """
        导入表单字段生成全局变量
        """
        global_field_ids = []
        for data in data_struct.values():
            for item in data["items"]:
                worksheet_id = item.pop("worksheet_id")
                worksheet_key = data["key"]
                worksheet_name = data["name"]
                field_key = item.pop("key")

                key = uuid.uuid3(uuid.uuid1(), uuid.uuid4().hex).hex
                if key[0].isdigit():
                    # 开头为数字，重新生成
                    first_letter = random.choice(string.ascii_letters)
                    key = first_letter + key[1:]

                if item["type"] not in GlobalVariable.TYPE_CHOICES:
                    item["type"] = "STRING"

                if isinstance(item["meta"], str):
                    item["meta"] = json.loads(item["meta"])
                item["meta"].update(
                    {
                        "worksheet": {
                            "id": worksheet_id,
                            "key": worksheet_key,
                            "name": worksheet_name,
                            "field_key": field_key,
                        },
                    }
                )
                global_field_data = {
                    "key": key,
                    "name": item["name"],
                    "type": item["type"],
                    "state_id": state.id,
                    "flow_id": state.workflow_id,
                    "meta": item["meta"],
                }
                fields_object = GlobalVariable.objects.filter(
                    state_id=state.id, is_deleted=False
                ).values("id", "meta")
                exist_flag = None
                for field in fields_object:
                    exist_flag = self.import_fields_repeat_check(field, field_key)
                    if exist_flag:
                        break
                if exist_flag:
                    continue
                else:
                    # 默认值联动规则中有不可修改选
                    field = GlobalVariable.objects.create(**global_field_data)
                    logger.info("新增流程全局字段id：{field}".format(field=field.id))
                    global_field_ids.append(field.id)
        return global_field_ids

    def copy_fields_from_worksheet_field(self, worksheet_field_ids, state, service):
        """
        流程内导入字段
        """
        logger.info("表单导入字段id列表：{field_ids}".format(field_ids=worksheet_field_ids))

        data_struct = self._create_fields_struct(worksheet_field_ids)

        field_ids = self._create_workflow_fields(data_struct, state, service)

        logger.info(
            "节点{state}原始绑定字段：{fields}".format(state=state.id, fields=state.fields)
        )
        state.fields.extend(field_ids)
        logger.info(
            "节点{state}插入新增字段：{fields}".format(state=state.id, fields=state.fields)
        )

        new_fields = list(set(state.fields))
        logger.info("创建new_fields列表：{new_fields}".format(new_fields=new_fields))

        state.fields = new_fields
        state.save()
        state_change_project_change(state)
        logger.info(
            "节点{state}保存设置后，字段列表：{fields}".format(state=state.id, fields=state.fields)
        )
        return field_ids

    def create_global_field_from_worksheet(self, worksheet_field_ids, state):
        """
        表单字段生成全局变量
        """
        logger.info("表单导入字段id列表：{field_ids}".format(field_ids=worksheet_field_ids))
        data_struct = self._create_fields_struct(worksheet_field_ids)
        global_fields_ids = self._create_global_field(data_struct, state)
        return global_fields_ids
