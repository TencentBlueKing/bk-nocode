# -*- coding: utf-8 -*-
from itsm.component.exceptions import WorkFlowNotFoundError
from itsm.workflow.models import Workflow, Field
from itsm.workflow.serializers import FieldVariablesGroupSerializer, StateSerializer


class WorkFlowHandler:
    def __init__(self, workflow_id=None):
        self.workflow_id = workflow_id
        self.obj = None
        super(WorkFlowHandler, self).__init__()

    def _get_instance(self):
        try:
            obj = Workflow.objects.get(id=self.workflow_id)
        except Workflow.DoesNotExist:
            raise WorkFlowNotFoundError()
        return obj

    def _group(self, fields_data):
        state_dict = dict()
        for item in fields_data:
            if item.get("state"):
                if item["state"] in state_dict:
                    state_dict[item["state"]]["fields"].append(item)
                else:
                    state_dict.setdefault(item.get("state"), {})
                    state_dict[item["state"]].setdefault("state_id", item["id"])
                    state_dict[item["state"]].setdefault("state_name", item["state"])
                    state_dict[item["state"]].setdefault("fields", [])
                    state_dict[item["state"]]["fields"].append(item)
                item.pop("id")
                item.pop("state")
        return state_dict.values()

    @property
    def instance(self):
        if self.obj is None:
            self.obj = self._get_instance()
        return self.obj

    def workflow_all_fields(self, workflow):
        all_states = workflow.states.all().exclude(type__in=["START", "END"])
        all_fields = []
        for state in all_states:
            field_ids = state.fields
            field_queryset = Field.objects.filter(id__in=field_ids, workflow=workflow)
            fields_data = FieldVariablesGroupSerializer(field_queryset, many=True).data
            data = self._group(fields_data)
            all_fields += data
        return all_fields

    def workflow_all_states(self, workflow):
        all_states = workflow.states.all().exclude(type__in=["START", "END"])
        data = StateSerializer(all_states, many=True).data
        return data
