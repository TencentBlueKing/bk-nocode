# -*- coding: utf-8 -*-
from itsm.component.exceptions import StateNotFoundError
from itsm.workflow.models import State


class StateHandler:
    def __init__(self, state_id=None):
        self.state_id = state_id
        self.obj = None
        super(StateHandler, self).__init__()

    def _get_instance(self):
        try:
            obj = State.objects.get(id=self.state_id)
        except State.DoesNotExist:
            raise StateNotFoundError()
        return obj

    @property
    def instance(self):
        if self.obj is None:
            self.obj = self._get_instance()
        return self.obj
