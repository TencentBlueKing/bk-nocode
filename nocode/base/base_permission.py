# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-NOCODE SMAKER蓝鲸无代码平台  available.

Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.

BK-NOCODE 蓝鲸无代码平台(S-maker) is licensed under the MIT License.

License for BK-NOCODE 蓝鲸无代码平台(S-maker) :
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
from django.conf import settings
from rest_framework import permissions
from django.utils.translation import ugettext as _

from common.log import logger
from config.default import BK_IAM_SYSTEM_ID
from iam import IAM, Subject, Action, Resource, MultiActionRequest
from iam.exceptions import AuthFailedException
from itsm.project.handler.project_handler import ProjectHandler
from nocode.base.basic import check_user_owner_creator
from nocode.project_manager.handlers.project_version_handler import (
    ProjectVersionModelHandler,
)


class PageDesignPermission(permissions.BasePermission):
    message = _("您没有该应用操作的权限")

    def has_permission(self, request, view):
        if view.action == "create":
            project_key = request.data.get("project_key")
            if project_key is None:
                return False
            project = ProjectHandler(project_key=project_key).instance
            user = request.user
            return check_user_owner_creator(user=user, project=project)
        return True

    def has_object_permission(self, request, view, obj, **kwargs):
        project = ProjectHandler(project_key=obj.project_key).instance
        user = request.user
        if view.action in ["update", "destroy"]:
            return check_user_owner_creator(user=user, project=project)
        return True


class BasePermission(object):
    def __init__(self, request):
        self.request = request
        self._iam = IAM(
            settings.APP_CODE,
            settings.SECRET_KEY,
            settings.BK_IAM_INNER_HOST,
            settings.BK_IAM_ESB_PAAS_HOST,
        )

    def get_action_name(self, project_key, action_id):
        def get_action_id_map(data):
            action_map = {}
            for values in data.values():
                for item in values:
                    if item["type"] == "LIST":
                        button_group = item["config"].get("buttonGroup", [])
                        option_list = item["config"].get("optionList", [])
                        for button in button_group + option_list:
                            if "id" not in button:
                                continue
                            action_map[button["id"]] = button["name"]
                    if item["type"] == "FUNCTION":
                        action_map[str(item["id"])] = item["config"].get("name", "")
                    if item["type"] == "SHEET":
                        action_map[str(item["id"])] = "提交"
            return action_map

        project = ProjectHandler(project_key=project_key).instance
        version_handler = ProjectVersionModelHandler(
            project_key=project_key, version_number=project.version_number
        )
        page_components = version_handler.instance.page_component

        action_map = get_action_id_map(page_components)
        return action_map.get(str(action_id), "")

    def have_create_ticket_permit(self, project_key, action_id, page_id):
        if self.have_project_admin_permit(project_key):
            return True

        apply_actions = ["action_execute"]

        subject = Subject(
            "user", self.request.user.username if self.request else self.username
        )
        actions = [Action(action) for action in apply_actions]

        bk_iam_path = "/project,{}/page,{}/".format(project_key, page_id)
        resources = [
            Resource(
                BK_IAM_SYSTEM_ID,
                "action",
                str(action_id),
                {
                    "iam_resource_owner": "",
                    "_bk_iam_path_": bk_iam_path,
                    "name": self.get_action_name(project_key, action_id),
                },
            )
        ]
        request = MultiActionRequest(
            BK_IAM_SYSTEM_ID, subject, actions, resources, None
        )
        try:
            auth_actions = self._iam.resource_multi_actions_allowed(request)
            logger.info("正在向权限中心获取权限,auth_actions={}".format(auth_actions))
        except BaseException as error:
            logger.info("权限中心获取权限出错,error={}".format(error))
            auth_actions = {}

        if self.auth_result(auth_actions, apply_actions):
            return True

        no_permission_actions = [
            action for action, result in auth_actions.items() if not result
        ]
        logger.info("no_permission_actions is ={}".format(no_permission_actions))

        raise AuthFailedException(
            settings.APP_CODE,
            Subject("user", self.request.user.username),
            Action(no_permission_actions[0]),
            resources,
        )

    def have_project_create_permit(self):
        apply_actions = ["project_create"]
        subject = Subject(
            "user", self.request.user.username if self.request else self.username
        )
        actions = [Action(action) for action in apply_actions]
        resources = []
        request = MultiActionRequest(
            BK_IAM_SYSTEM_ID, subject, actions, resources, None
        )
        try:
            auth_actions = self._iam.resource_multi_actions_allowed(request)
        except BaseException as error:
            logger.info("权限中心获取权限出错,error={}".format(error))
            auth_actions = {}

        if self.auth_result(auth_actions, apply_actions):
            return True
        return False

    def have_project_admin_permit(self, project_key):
        """查看是否有应用超级管理员的权限"""
        apply_actions = ["project_admin"]
        subject = Subject(
            "user", self.request.user.username if self.request else self.username
        )
        actions = [Action(action) for action in apply_actions]

        bk_iam_path = "/project,{}/".format(project_key)
        resources = [
            Resource(
                BK_IAM_SYSTEM_ID,
                "project",
                str(project_key),
                {
                    "iam_resource_owner": "",
                    "_bk_iam_path_": bk_iam_path,
                    "name": "",
                },
            )
        ]
        request = MultiActionRequest(
            BK_IAM_SYSTEM_ID, subject, actions, resources, None
        )
        try:
            auth_actions = self._iam.resource_multi_actions_allowed(request)
        except BaseException as error:
            logger.info("权限中心获取权限出错,error={}".format(error))
            auth_actions = {}

        if self.auth_result(auth_actions, apply_actions):
            return True

        return False

    def have_page_access_resource(self, project_key, page_id):

        if self.have_project_admin_permit(project_key):
            return True

        apply_actions = ["page_view"]

        subject = Subject(
            "user", self.request.user.username if self.request else self.username
        )
        actions = [Action(action) for action in apply_actions]

        resources = [
            Resource(
                BK_IAM_SYSTEM_ID,
                "page",
                str(page_id),
                {
                    "iam_resource_owner": "",
                    "_bk_iam_path_": "/project,{}/".format(project_key),
                    "name": "",
                },
            )
        ]
        request = MultiActionRequest(
            BK_IAM_SYSTEM_ID, subject, actions, resources, None
        )
        try:
            auth_actions = self._iam.resource_multi_actions_allowed(request)
            logger.info("正在向权限中心获取权限,auth_actions={}".format(auth_actions))
        except BaseException as error:
            logger.info("权限中心获取权限出错,error={}".format(error))
            auth_actions = {}

        if self.auth_result(auth_actions, apply_actions):
            return True

        no_permission_actions = [
            action for action, result in auth_actions.items() if not result
        ]
        logger.info("no_permission_actions is ={}".format(no_permission_actions))

        raise AuthFailedException(
            settings.APP_CODE,
            Subject("user", self.request.user.username),
            Action(no_permission_actions[0]),
            resources,
        )

    @staticmethod
    def auth_result(auth_actions, actions):
        """
        认证结果解析
        """
        denied_actions = []
        for action, result in auth_actions.items():
            if action in actions and result is False:
                denied_actions.append(action)
        return len(denied_actions) == 0
