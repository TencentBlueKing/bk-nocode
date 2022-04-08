# -*- coding: utf-8 -*-
from itsm.ticket.models import Ticket, TicketGlobalVariable
from itsm.workflow.models import GlobalVariable
from nocode.data_engine.core.managers import DataManager
from nocode.data_engine.core.utils import ConditionTransfer
from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import Service


class DataQueryService(Service):
    __need_schedule__ = False
    __multi_callback_enabled__ = False

    def get_response_data(self, page_queryset):
        """
        查询到的值去掉contents__前缀
        """
        data = []
        for item in page_queryset:
            new_item = {}
            for key, value in item.items():
                new_item[key.replace("contents__", "", 1)] = value
            data.append(new_item)

        return data

    def get_keys(self, fields):
        keys = []
        for field in fields:
            keys.append("contents__{}".format(field))
        return keys

    def convert_conditions(self, conditions):
        transfer = ConditionTransfer(conditions)
        return transfer.trans()

    def worksheet_data_query(self, state, workflow_global_fields):
        worksheet_id = state["extras"]["worksheet_id"]
        conditions = state["extras"].get("conditions", {})

        fields = []
        for item in workflow_global_fields.values_list("meta", flat=True):
            if not item.get("worksheet"):
                continue
            fields.append(item["worksheet"]["field_key"])

        keys = self.get_keys(fields)

        manager = DataManager(worksheet_id)

        queryset = manager.get_queryset()
        filters = self.convert_conditions(conditions)

        queryset = queryset.filter(filters).values(*keys)

        if not queryset:
            return

        data = self.get_response_data(queryset)
        query_data = {}
        for item in workflow_global_fields:
            if not item.meta.get("worksheet"):
                continue
            query_data.setdefault(
                item.key, data[0].get(item.meta["worksheet"]["field_key"], "")
            )
        return query_data

    def ticket_global_fields_create(self, workflow_global_fields, state_id, ticket_id):
        fields = [
            TicketGlobalVariable(
                key=item.key,
                name=item.name,
                state_id=state_id,
                ticket_id=ticket_id,
                value="",
            )
            for item in workflow_global_fields
        ]
        TicketGlobalVariable.objects.bulk_create(fields)

        return TicketGlobalVariable.objects.filter(
            state_id=state_id,
            ticket_id=ticket_id,
        )

    def execute(self, data, parent_data):
        ticket_id = parent_data.inputs.ticket_id
        state_id = data.inputs.state_id

        ticket = Ticket.objects.get(id=ticket_id)
        state = ticket.flow.get_state(state_id)
        ticket.do_before_enter_state(state_id, by_flow=self.by_flow)
        workflow_global_fields = GlobalVariable.objects.filter(
            state_id=state_id, flow_id=state["workflow"]
        )

        ticket_global_fields = self.ticket_global_fields_create(
            workflow_global_fields, state_id, ticket_id
        )

        flag_field = TicketGlobalVariable.objects.get(
            key=f"data_query_result_{state_id}",
            name="数据是否存在",
            ticket_id=ticket_id,
        )

        # 单一数据查询默认查第一条
        query_data = self.worksheet_data_query(
            state=state, workflow_global_fields=workflow_global_fields
        )
        if not query_data:
            flag_field.value = "false"
            flag_field.save()
            return True

        for item in ticket_global_fields:
            if item.key in query_data:
                item.value = query_data[item.key]
            if item.key == f"data_query_result_{state_id}":
                item.value = "true"
            item.save()

        data.set_outputs("query_data", query_data)
        return True


class NormalTaskComponent(Component):
    name = "单一数据查询"
    code = "data_query"
    bound_service = DataQueryService
