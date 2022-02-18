# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.

Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.

BK-ITSM 蓝鲸流程服务 is licensed under the MIT License.

License for BK-ITSM 蓝鲸流程服务:
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

from django.utils.translation import ugettext as _

from itsm.trigger.action.core.component import BaseComponent
from itsm.trigger.action.core import BaseForm, JSONField
from itsm.ticket.models import Ticket
from itsm.component.constants import TASK_SIGNAL

__register_ignore__ = False


class FieldForms(BaseForm):
    """
    发送通知的输入数据格式
    """

    field_groups = JSONField(name=_("填充的字段组"))


class ModifyPublicFieldComponent(BaseComponent):
    name = _("填充字段值")
    code = "fill_fields"
    is_async = False
    form_class = FieldForms
    exclude_signal_type = [TASK_SIGNAL]

    def _execute(self):
        try:
            dst_ticket = Ticket.objects.get(sn=self.context.get("ticket_sn"))
        except Ticket.DoesNotExist:
            self.data.set_outputs(
                "message", _("对应的单据【{}】不存在".format(self.context.get("ticket_sn")))
            )
            return False
        dst_ticket.refresh_from_db()

        outputs = []
        field_groups = self.data.inputs["field_groups"]
        update_fields_set = set()
        for group, item in field_groups.items():
            dst_field_key, dst_field_value = "", ""
            for value in item:
                if value["key"] == "field_key":
                    dst_field_key = value["value"]
                if value["key"] == "field_value":
                    dst_field_value = value["value"]
            dst_fields = dst_ticket.fields.filter(key=dst_field_key)
            if dst_fields.exists():
                dst_fields.update(_value=dst_field_value)
                first_field = dst_fields.first()
                outputs_data = {
                    "field_key__display": first_field.name,
                    "field_value__display": first_field.display_value,
                }
                outputs.append({group: outputs_data})
                update_fields_set.add(dst_field_key)
            if dst_field_key in ["bk_biz_id", "current_status", "title"]:
                setattr(dst_ticket, dst_field_key, dst_field_value)
                update_fields_set.add(dst_field_key)

        dst_ticket.save(update_fields=list(update_fields_set))
        self.data.set_outputs("field_groups", outputs)
        return True
