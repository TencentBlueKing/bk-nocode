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

from django.http import Http404
from itsm.component.drf.permissions import IamAuthPermit
from itsm.component.constants.trigger import SOURCE_WORKFLOW
from itsm.workflow.models import Workflow


class WorkflowTriggerPermit(IamAuthPermit):
    @staticmethod
    def get_flow_or_raise_error(workflow_id):
        try:
            return Workflow.objects.get(id=workflow_id)
        except Workflow.DoesNotExist:
            raise Http404("对应的流程不存在，无法操作")

    @staticmethod
    def create_trigger_from_workflow(request, view):
        return (
            view.action == "create"
            and request.data.get("source_type") == SOURCE_WORKFLOW
        )

    @staticmethod
    def clone_trigger_to_workflow(request, view):
        return (
            view.action == "clone"
            and request.data.get("dst_source_type") == SOURCE_WORKFLOW
        )

    def has_permission(self, request, view):
        return True

    # def has_object_permission(self, request, view, obj):
    #     if not obj.source_type == SOURCE_WORKFLOW:
    #         # 非流程来源的，更新做流程元素管理的权限
    #         return self.iam_auth(request, apply_actions=[], obj=obj)
    #
    #     # 与流程相关的，走流程的权限
    #     apply_action = ["workflow_manage"]
    #     return self.iam_auth(request, apply_action, self.get_flow_or_raise_error(obj.source_id))

    def has_object_permission(self, request, view, obj, **kwargs):
        return True
