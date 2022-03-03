# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-NOCODE SMAKER蓝鲸无代码平台  available.

Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.

BK-NOCODE SMAKER蓝鲸无代码平台 is licensed under the MIT License.

License for BK-NOCODE SMAKER蓝鲸无代码平台 :
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
import copy
import datetime
import json
import logging
import re

from django.db import IntegrityError

from itsm.component.constants import (
    ADD_STATE,
    UPDATE_STATE,
    DELETE_STATE,
    VALUE_FROM_FIELD,
    SYSTEM_OPERATE,
    INCREMENT,
    REDUCTION,
    SYSTEM,
    APPROVER,
    FIELD_INCREMENT,
    FIELD_REDUCTION,
    LEADER,
)
from itsm.ticket.models import (
    Ticket,
    get_user_leader,
    Status,
    SignTask,
    TicketGlobalVariable,
)
from nocode.data_engine.core.managers import DataManager
from nocode.data_engine.core.utils import ConditionTransfer
from nocode.data_engine.core.constants import (
    EXPRESSION_KEYWORD,
    TYPE_KEYWORD,
    ALLOWED_EXPRESSION_TYPE_KEY,
)
from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import Service

logger = logging.getLogger("celery")


class StateExtraManager:
    def __init__(self, state, ticket):
        self.state_instance = state
        self.ticket = ticket
        self.field_queryset = ticket.fields.all()

    @property
    def data_manager_info(self):
        return self.state_instance["extras"].get("dataManager", {})

    def get_field_value(self, key):
        """
        :param key: 字段键
        :param field_queryset: Ticket Fields QuerySet
        """
        try:
            field_inst = self.field_queryset.filter(key=key).first()
            if field_inst.type == "INT":
                return int(field_inst.value)
            return field_inst.value
        except Exception:
            field_inst = TicketGlobalVariable.objects.filter(
                key=key, ticket_id=self.ticket.id
            ).first()
            if field_inst is not None:
                return field_inst.value
            return None

    def get_system_field_value(self, value_type):
        # 这边应该拆分类了
        # 当前日期
        value_selector = {
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "creator": self.ticket.creator,
            "start_time": self.ticket.create_at.strftime("%Y-%m-%d %H:%M:%S"),
            "leader": ",".join(get_user_leader(self.ticket.creator)),
            "sn": self.ticket.sn,
        }
        if value_type in value_selector:
            return value_selector[value_type]

    def get_approver_field_value(self, value):
        try:
            status = Status.objects.get(ticket_id=self.ticket.id, state_id=value)
            sign_tasks = SignTask.objects.filter(status_id=status.id)
            processors = [task.processor for task in sign_tasks]
            return ",".join(processors)
        except Exception:
            return ""

    def get_leader(self, key):
        """
        获取指定字段的上级
        """
        try:
            field_inst = self.field_queryset.filter(key=key).first()
            if field_inst.type != "MEMBER":
                logger.info(
                    "[DataProcessingService][get_leader] 获取指定字段上级失败, 当前字段非人员选择器字段"
                )
                return ""

            leaders = get_user_leader(field_inst.value)
            return ",".join(leaders)
        except Exception as e:
            logger.info(
                "[DataProcessingService][get_leader] 获取指定字段上级失败, 发生异常, error={}".format(
                    e
                )
            )
            return ""

    def make_mapping(
        self,
    ):
        """
        :param field_queryset: Ticket Fields QuerySet
        :param mapping: 字段映射
        mapping = [
            {"key": "username", "type": "field", "value": "${param_username}"},
            {"key": "staff", "type": "const", "value": "employee"},
        ]
        """
        mapping = self.data_manager_info.get("mapping", [])
        method_select = {
            SYSTEM: self.get_system_field_value,
            APPROVER: self.get_approver_field_value,
        }
        data = {}
        for mi in mapping:
            if mi["type"] in [INCREMENT, REDUCTION]:
                continue
            # 从引用变量中取值
            elif mi["type"] in [
                VALUE_FROM_FIELD,
                FIELD_INCREMENT,
                FIELD_REDUCTION,
                LEADER,
            ]:
                params = re.findall(r"\${param_(.*?)}", mi["value"])
                if mi["type"] == LEADER:
                    value = self.get_leader(params[0])
                else:
                    value = self.get_field_value(params[0])

            elif mi["type"] in method_select:
                value = method_select.get(mi["type"])(mi["value"])

            else:
                value = mi["value"]
            data[mi["key"]] = value
        return data

    def map_data(self):
        return self.make_mapping()

    def compute_field(self, compute_fields, data):
        data = copy.deepcopy(data)
        for item in compute_fields:
            # 常量 引用变量 进行增减
            if item["type"] in [INCREMENT, FIELD_INCREMENT]:
                data[item["key"]] = data[item["key"]] + int(item["value"])
            if item["type"] in [REDUCTION, FIELD_REDUCTION]:
                data[item["key"]] = data[item["key"]] - int(item["value"])

        return data

    def get_compute_field(self):
        data = []
        for mi in self.data_manager_info.get("mapping", []):
            if mi["type"] in [INCREMENT, REDUCTION, FIELD_INCREMENT, FIELD_REDUCTION]:
                data.append(mi)
        return data

    def make_expressions(self, expressions):
        data = []
        for expression in expressions:
            if expression.get(TYPE_KEYWORD, None) != ALLOWED_EXPRESSION_TYPE_KEY:
                params = re.findall(r"\${param_(.*?)}", expression["value"])
                value = self.get_field_value(params[0])
                if params[0] == "ids" and not isinstance(value, list):
                    value = json.loads(value)
                if value is None:
                    try:
                        value = TicketGlobalVariable.objects.get(
                            key=params[0], ticket_id=self.ticket.id
                        ).value
                    except Exception:
                        return None
                expression.update(
                    {
                        "type": ALLOWED_EXPRESSION_TYPE_KEY,
                        "value": value,
                    }
                )
            data.append(expression)
        return data

    def conditions(self):
        conditions = self.data_manager_info.get("conditions")
        if conditions:
            conditions[EXPRESSION_KEYWORD] = self.make_expressions(
                conditions.get(EXPRESSION_KEYWORD, [])
            )
            conditions = ConditionTransfer(conditions).trans()
        return conditions

    def update_info(self, instance_id):
        instance, created = TicketGlobalVariable.objects.get_or_create(
            key="data_proc_result_%s" % self.state_instance["id"],
            name="data_proc_result_%s" % self.state_instance["id"],
            state_id=self.state_instance["id"],
            ticket_id=self.ticket.id,
            value="",
        )
        instance.value = instance_id
        instance.save()


class DataProcessingService(Service):
    __need_schedule__ = False
    __multi_callback_enabled__ = False

    def execute(self, data, parent_data):
        logger.info(
            "DataProcessingService execute: data={}, parent_data={}".format(
                data.inputs, parent_data.inputs
            )
        )

        # 节点信息准备
        ticket_id = parent_data.inputs.ticket_id
        ticket = Ticket._objects.get(id=ticket_id)
        state_id = data.inputs.state_id
        state = ticket.flow.get_state(state_id)
        ticket.do_before_enter_state(state_id, by_flow=self.by_flow)
        current_node = ticket.node_status.get(state_id=state_id)
        action_map = {"ADD": "新增", "EDIT": "更新", "DELETE": "删除"}

        # 获取字段信息
        # 操作方法 action = "add" / "delete" / "update"
        # 匹配条件 conditions 见 nocode/data_engine/core/utils.py 的 ConditionTransfer.__init__ 参数
        # 目标表 worksheet_id
        # 映射关系 mapping = [
        #     {"key": "username", "type": "field", "value": "${param_username}"},
        #     {"key": "staff", "type": "const", "value": "employee"},
        # ]

        state_extra_manager = StateExtraManager(state=state, ticket=ticket)
        data_manager_info = state_extra_manager.data_manager_info
        action = data_manager_info.get("action")
        action_name = action_map.get(action, "")
        worksheet_id = data_manager_info.get("worksheet_id")

        map_data = state_extra_manager.map_data()
        compute_fields = state_extra_manager.get_compute_field()

        # 获取查询条件
        conditions = state_extra_manager.conditions()

        # 获取对应工作表的manager对象
        manager = DataManager(worksheet_id)

        # 获取操作人
        operator = ticket.creator.replace(",", "")

        # 初始化日志
        log_data = copy.deepcopy(data_manager_info)
        log_data.update({"map_data": map_data})
        is_failed = False

        # 记录celery日志
        logger.info("DataProcessingService Operate by {}".format(operator))

        try:
            # 添加操作
            if action == ADD_STATE:
                obj = manager.add(map_data, operator)
                logger.info(
                    "DataProcessingService Data Add Success (id={})".format(obj.id)
                )
                state_extra_manager.update_info(instance_id=obj.id)
                current_node.create_action_log(
                    "system",
                    "正在执行新增操作，此次成功新增了一条数据，id={}".format(obj.id),
                    source=SYSTEM_OPERATE,
                    action_type=SYSTEM_OPERATE,
                    fields=log_data,
                )
            # 更新操作
            elif action == UPDATE_STATE:
                worksheets = manager.get_queryset().filter(conditions)
                current_node.create_action_log(
                    "system",
                    "正在执行更新操作，检测到有{}条数据需要更新".format(len(worksheets)),
                    source=SYSTEM_OPERATE,
                    action_type=SYSTEM_OPERATE,
                    fields=log_data,
                )
                for ws in worksheets:
                    ws_id = ws.id
                    data = copy.deepcopy(ws.contents)
                    data = state_extra_manager.compute_field(compute_fields, data)
                    data.update(map_data)
                    manager.update(ws_id, data, operator)
                    logger.info(
                        "DataProcessingService Data Update Success (id={})".format(
                            ws_id
                        )
                    )
            # 删除操作
            elif action == DELETE_STATE:
                worksheets = manager.get_queryset().filter(conditions)
                current_node.create_action_log(
                    "system",
                    "正在执行删除操作，检测到有{}条数据需要删除".format(len(worksheets)),
                    source=SYSTEM_OPERATE,
                    action_type=SYSTEM_OPERATE,
                    fields=log_data,
                )
                for ws in worksheets:
                    ws_id = ws.id
                    manager.delete(ws_id)
                    logger.info(
                        "DataProcessingService Data Delete Success (id={})".format(
                            ws_id
                        )
                    )
        except IntegrityError as e:
            is_failed = True
            if "(1062" in str(e):
                log_data.update({"err": "数据唯一性索引失败，不能插入相同的数据，数据库报错 error={}".format(e)})
                current_node.set_failed_status(
                    message="数据处理失败，设置了唯一性索引的字段不能重复写入，数据库报错 error={}".format(e)
                )
            else:
                log_data.update({"err": str(e)})
                # 当前节点设置为失败
                current_node.set_failed_status(message="数据处理节点发生异常，error= {}".format(e))
        except Exception as err:
            if is_failed:
                pass
            import traceback

            traceback.print_exc()
            log_data.update({"err": str(err)})
            # 当前节点设置为失败
            current_node.set_failed_status(message="数据处理节点发生异常，error= {}".format(err))
            is_failed = True

        current_node.create_action_log(
            "system",
            "数据处理节点{}操作执行{}".format(action_name, "失败" if is_failed else "成功"),
            source=SYSTEM_OPERATE,
            action_type=SYSTEM_OPERATE,
            fields=log_data,
        )
        if is_failed:
            error_message = "DataProcessingService exit with err: {}"
            logger.info(error_message.format(log_data.get("err")))
            # 终止单据
            ticket.failed(
                state_id=state_id,
                failed_message=error_message.format(log_data.get("err")),
            )
            return False
        logger.info("DataProcessingService exit without err")
        return True


class NormalTaskComponent(Component):
    name = "数据处理"
    code = "data_processing"
    bound_service = DataProcessingService
