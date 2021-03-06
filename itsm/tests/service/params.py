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


CREATE_SERVICE_DATA = {
    "type": "ADD",
    "name": "test",
    "desc": "test",
    "project_key": "test",
}

# CONFIGS = {
#     'workflow_config': {
#         'is_revocable': True,
#         'revoke_config': {'type': 2, 'state': 0},
#         # 'is_supervise_needed': False,
#         # 'supervise_type': 'EMPTY',
#         # 'supervisor': '',
#         'notify': [],
#         'notify_rule': 'NONE',
#         'notify_freq': 0},
#     'display_type': 'OPEN',
#     'can_ticket_agency': False
# }

CONFIGS = {
    "workflow_config": {
        "notify": [],
        "notify_freq": 0,
        "notify_rule": "NONE",
        "revoke_config": {"type": 2, "state": 0},
        "is_revocable": "true",
        "show_all_workflow": "true",
        "show_my_create_workflow": "true",
    }
}
