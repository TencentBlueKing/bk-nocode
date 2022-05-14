# -*- coding: utf-8 -*-
import copy
import operator
import re

from celery.task import task

from common.log import logger
from itsm.service.models import Service
from itsm.ticket.serializers import TicketSerializer
from itsm.ticket.tasks import start_pipeline
from itsm.trigger.signal import event_execute

from nocode.data_engine.core.utils import ConditionTransfer
from nocode.worksheet.handlers.project_version_handler import ProjectVersionHandler


class WorkSheetEventExecute:
    def __init__(self, action_type, worksheet_id, record_contents, project_key):
        self.action_type = action_type
        self.worksheet_id = worksheet_id
        self.record_contents = record_contents
        self.project_key = project_key

    def create_ticket(self, data):
        try:
            logger.info("[worksheet_event_start] 正在准备创建单据，data={}".format(data))
            serializer = TicketSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
        except Exception as e:
            logger.info(
                "[worksheet_event_start] 表单触发单据创建异常，error={}, data={}".format(e, data)
            )
            return False

        try:
            logger.info("[worksheet_event_start] 单据创建完成，正在初始化单据字段，data={}".format(data))
            instance.do_after_create(data["fields"], None)
        except Exception as e:
            logger.info(
                "[worksheet_event_start] 初始化单据字段异常，error={}, data={}".format(e, data)
            )
            instance.delete()
            logger.info(
                "[worksheet_event_start] 异常单据已经删除，ticket_id={}, sn={}".format(
                    instance.id, instance.sn
                )
            )
            return False

        start_pipeline.apply_async([instance])
        return True

    def restore_fields(self, service, content):
        field_ids = service.workflow.first_state["fields"]
        fields = []
        for field_id in field_ids:
            version_field = service.workflow.get_field(field_id)
            # 忽略错误的id
            if version_field is None:
                continue
            field = copy.deepcopy(version_field)
            default = field.get("default")

            data = {}
            worksheet_value = None
            if field["meta"].get("worksheet"):
                worksheet_value = content.get(field["meta"]["worksheet"]["field_key"])
            # 字段结构组装
            data.setdefault("id", field["id"])
            data.setdefault("type", field["type"])
            data.setdefault("choice", field["choice"])
            data.setdefault("key", field["key"])
            data.setdefault(
                "value",
                default if not field["meta"].get("worksheet") else worksheet_value,
            )

            fields.append(data)
        return fields

    def convert_conditions(self, conditions, record_content):
        transfer = ConditionTransfer(conditions)
        operator_map = {
            "==": operator.eq,
            ">": operator.gt,
            "<": operator.lt,
            ">=": operator.ge,
            "<=": operator.lt,
            "in": operator.contains,
        }
        transfer.trans()
        connector = conditions["connector"]
        expression_result = []
        for item in conditions["expressions"]:
            if item["condition"] == "icontains":
                result = re.findall(
                    f".*?{item['value']}.*?", record_content[item["key"]], re.I | re.S
                )
                flat = True if result else False
            else:
                flat = operator_map[item["condition"]](
                    record_content[item["key"]], item["value"]
                )
            expression_result.append(flat)
        return (
            all(expression_result)
            if connector.upper() == "AND"
            else any(expression_result)
        )

    def events_execute(self):
        # worksheet_id=self.worksheet_id, action_type=self.action_type
        worksheet_events = ProjectVersionHandler(
            project_key=self.project_key
        ).get_worksheet_events(worksheet_id=self.worksheet_id)

        suitable_events = [
            item for item in worksheet_events if item["action_type"] == self.action_type
        ]

        if not suitable_events:
            logger.info(f"表单：{self.worksheet_id}的{self.action_type}操作没有自动化功能触发")
            return True

        for event in suitable_events:
            conditions = event["conditions"]
            if conditions:
                flag = self.convert_conditions(conditions, self.record_contents)
                if not flag:
                    logger.info(f"表单记录{self.record_contents}不满足触发条件")
                    return True
            service_id = event["service_id"]
            service = Service.objects.get(id=service_id)

            fields = self.restore_fields(service, self.record_contents)
            data = {"service_id": service_id, "fields": fields, "creator": "auto"}

            flag = self.create_ticket(data)
            if not flag:
                logger.error(
                    f"表单触发功能执行失败: serivce: {service_id}, data: {data}, worksheet: {self.worksheet_id}"
                )
                return False
        logger.info(f"表单触发功能执行, {worksheet_events.values('service_id')}")
        return True

    def __call__(self, *args, **kwargs):
        self.events_execute()


@task
def worksheet_event_start(
    worksheet_id, record_contents, action, project_key, *args, **kwargs
):
    WorkSheetEventExecute(
        worksheet_id=worksheet_id,
        record_contents=record_contents,
        action_type=action,
        project_key=project_key,
    )()


def execute(sender, **kwargs):
    content = kwargs.get("content")
    worksheet_event_start.apply_async(
        (
            content["worksheet_id"],
            content["record_contents"],
            content["action"],
            content["project_key"],
        )
    )


event_execute.connect(execute)
