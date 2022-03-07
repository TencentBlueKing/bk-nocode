# -*- coding: utf-8 -*-
import json
import uuid

from common.log import logger
from itsm.workflow.models import Field

from itsm.workflow.signals.handlers import state_change_project_change
from nocode.base.basic import ignore_fields_type
from nocode.worksheet.exceptions import WorkSheetFieldDoesNotExist
from nocode.worksheet.handlers.worksheet_field_handler import WorkSheetFieldModelHandler
from nocode.worksheet.handlers.worksheet_handler import WorkSheetModelHandler


class WorkSheetFieldModelHandler(WorkSheetFieldModelHandler):
    def retrieve(self, worksheet_field_id):
        return self.filter(pk=worksheet_field_id).first()

    def copy_fields_from_worksheet_field(self, worksheet_field_ids, state, service):
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

        field_ids = []
        failed_fields = []
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
                item["key"] = uuid.uuid3(uuid.uuid1(), uuid.uuid4().hex).hex
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
                    if field["meta"].get("worksheet"):
                        if field["meta"]["worksheet"]["field_key"] == field_key:
                            exist_flag = True
                            break
                if exist_flag:
                    continue
                else:
                    # 默认值联动规则中有不可修改选项
                    if item["meta"].get("data_config"):
                        if not item["meta"]["data_config"]["changeFields"]:
                            item["is_readonly"] = True
                    field = Field.objects.create(**item)
                    logger.info("新增流程字段id：{field}".format(field=field.id))
                    field_ids.append(field.id)

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
        return field_ids, failed_fields
