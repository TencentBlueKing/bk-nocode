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
from django.conf import settings
from rest_framework import permissions

from iam import Action, Resource, Subject
from iam.exceptions import AuthFailedException
from itsm.auth_iam.utils import IamRequest
from itsm.role.models import UserRole
from nocode.base.base_permission import BasePermission
from nocode.page.handlers.page_handler import PageOpenLinkHandler
from nocode.page.models import PageOpenRecord
from nocode.project_manager.handlers.project_version_handler import (
    ProjectVersionModelHandler,
)

from .models import Ticket


class SuperuserPermissionValidate(permissions.BasePermission):
    """
    超级管理员查看权限
    """

    def __init__(self):
        self.message = _("抱歉，您无权查看和操作")

    def has_object_permission(self, request, view, obj):
        username = request.user.username
        if UserRole.is_itsm_superuser(username):
            return True
        return False


class TicketPermissionValidate(permissions.BasePermission):
    """
    工单查看权限
    """

    def __init__(self):
        self.message = _("抱歉，您无权查看该单据")

    def has_permission(self, request, view):
        if view.action == "create_ticket":
            return self.have_create_ticket_permit(request)
        return True

    def has_object_permission(self, request, view, obj):
        return True

    def verify_token(self, request):
        token = request.data.get("token")
        service_id = request.data.get("service_id")
        if PageOpenRecord.objects.filter(token=token, service_id=service_id).exists():
            return True

        return False

    def have_create_ticket_permit(self, request):

        if "token" in request.data and self.verify_token(request):
            return True

        action_id = request.data.get("action_id")
        project_key = request.data.get("project_key")
        page_id = request.data.get("page_id")
        return BasePermission(request).have_create_ticket_permit(
            project_key, action_id, page_id
        )

    def iam_ticket_view_auth(self, request, obj):
        iam_client = IamRequest(request)
        resource_info = {
            "resource_id": str(obj.service_id),
            "resource_name": obj.service_name,
            "resource_type": "service",
        }

        apply_actions = ["ticket_view"]
        auth_actions = iam_client.resource_multi_actions_allowed(
            apply_actions, [resource_info], project_key=obj.project_key
        )
        if auth_actions.get("ticket_view"):
            return True

        bk_iam_path = "/project,{}/".format(obj.project_key)
        resources = [
            Resource(
                settings.BK_IAM_SYSTEM_ID,
                resource_info["resource_type"],
                str(resource_info["resource_id"]),
                {
                    "iam_resource_owner": resource_info.get("creator", ""),
                    "_bk_iam_path_": bk_iam_path
                    if resource_info["resource_type"] != "project"
                    else "",
                    "name": resource_info.get("resource_name", ""),
                },
            )
        ]

        raise AuthFailedException(
            settings.BK_IAM_SYSTEM_ID,
            Subject("user", request.user.username),
            Action(apply_actions[0]),
            resources,
        )


class StatePermissionValidate(permissions.BasePermission):
    def __init__(self):
        self.message = _("抱歉，您无权操作当前单据任务")

    def has_object_permission(self, request, obj):
        if (
            request.data.get("action_type") == "EXCEPTION_DISTRIBUTE"
            and request.user.is_superuser
        ):
            return True
        return obj.can_operate(request.user.username)


class EventLogPermissionValidate(permissions.BasePermission):
    def __init__(self):
        self.message = _("抱歉，您无权查看该单据的日志")

    def has_permission(self, request, view):

        if UserRole.is_itsm_superuser(request.user.username):
            return True

        if view.action in ["get_index_ticket_event_log", "get_my_deal_time"]:
            return True

        ticket_id = request.query_params.get("ticket")
        try:
            ticket = Ticket.objects.get(id=ticket_id)
        except Ticket.DoesNotExist:
            self.message = _("单据不存在：%s，请检查") % ticket_id
            return False

        return TicketPermissionValidate().has_object_permission(request, view, ticket)


class TicketFieldPermissionValidate(permissions.BasePermission):
    """
    目前FieldViewSet只使用了api_field_choices的方法
    """

    def __init__(self):
        self.message = _("抱歉，您无权限查看此信息")

    def has_permission(self, request, view):
        if UserRole.is_itsm_superuser(request.user.username):
            return True
        if view.action in ["api_field_choices", "download_file"]:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if UserRole.is_itsm_superuser(request.user.username):
            return True
        if view.action in ["api_field_choices", "download_file"]:
            return True
        return False


class FollowersNotifyLogPermissionValidate(permissions.BasePermission):
    def __init__(self):
        self.message = _("抱歉，您无权查看该单据的日志信息")

    def has_permission(self, request, view):
        params = request.query_params if request.method == "GET" else request.data

        ticket_id = params.get("ticket_id")
        try:
            ticket = Ticket.objects.get(id=ticket_id)
        except Ticket.DoesNotExist:
            self.message = _("抱歉，单据不存在：%s，请检查") % ticket_id
            return False

        return TicketPermissionValidate().has_object_permission(request, view, ticket)


class CommentPermissionValidate(permissions.BasePermission):
    def __init__(self):
        self.message = _("抱歉，您无权查看该单据的评价信息")

    def has_object_permission(self, request, view, obj):

        username = request.user.username

        if UserRole.is_itsm_superuser(username):
            return True

        if request.method in permissions.SAFE_METHODS:
            token = request.query_params.get("token")
            # 提单人或邀请评价能查看
            if obj.ticket.creator == username:
                return True
            if token and obj.ticket.is_email_invite_token(username, token):
                return True

        # 提单人或邀请评价才能从web评价
        if view.action == "update":
            token = request.data.get("token")
            self.message = _("抱歉，您不是该单据的提单人，无法评价")
            if obj.ticket.creator == username:
                return True
            if token and obj.ticket.is_email_invite_token(username, token):
                return True

        return False


class OperationalDataPermission(permissions.BasePermission):
    """运营数据权限，ITSM管理员，工单统计管理员"""

    def __init__(self):
        self.message = _("对不起，您没有模块的权限，请联系管理员。")

    def has_permission(self, request, view):
        username = request.user.username
        if UserRole.is_itsm_superuser(username) or UserRole.is_statics_manager(
            username
        ):
            return True
        return False


class FirstStateFieldsPermission(permissions.BasePermission):
    def __init__(self):
        self.paths = None
        self.page_type = None
        super(FirstStateFieldsPermission, self).__init__()

    def has_permission(self, request, view):
        self.paths = request.data["paths"]
        self.page_type = request.data["type"]
        # 路径校验, 白名单校验
        if not self.verify():
            return False
        return True

    @property
    def version(self):
        project_key = self.paths["project_key"]
        version_number = self.paths["version_number"]
        return ProjectVersionModelHandler(project_key, version_number).instance

    def check_page(self):
        page_id = self.paths["page_id"]
        return True if str(page_id) in self.version.page_component else False

    def check_page_component(self):

        for page_component in self.version.page_component[str(self.paths["page_id"])]:
            if self.paths["page_component_id"] == page_component["id"]:
                # 如果时列表类型，下潜到按钮
                if self.page_type.upper() == "LIST":
                    for button in page_component["config"][self.paths["source"]]:
                        if button["value"] == self.paths["service_id"]:
                            return True
                else:
                    if str(self.paths["service_id"]) == page_component["value"]:
                        return True
        return False

    def verify(self):
        # 先检测是否表单是否对外部开放, 是的话，跳过路径鉴权
        if PageOpenLinkHandler.open_record_exist(
            page_id=self.paths["page_id"], service_id=self.paths["service_id"]
        ):
            return True
        if not self.check_page():
            return False
        if not self.check_page_component():
            return False
        return True
