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

from common.log import logger
from config.default import BK_IAM_SYSTEM_ID
from iam import IAM, Subject, Action, MultiActionRequest, Resource
from nocode.permit.handlers.moudle_handler import ProjectVersionHandler


class PermitHandler:
    def __init__(self, project_key, request):
        self.project_key = project_key
        self._iam = IAM(
            settings.APP_CODE,
            settings.SECRET_KEY,
            settings.BK_IAM_INNER_HOST,
            settings.BK_IAM_ESB_PAAS_HOST,
        )
        self.request = request

    @property
    def version(self):
        return ProjectVersionHandler(project_key=self.project_key)

    def parse_tree(self, node, data):
        if node["type"] not in ["ROOT", "", "GROUP"]:
            data.append({"id": node["id"], "name": node["name"]})
        for item in node["children"]:
            self.parse_tree(item, data)

    def have_project_admin_permit(self):
        """查看是否有应用超级管理员的权限"""
        apply_actions = ["project_admin"]
        subject = Subject(
            "user", self.request.user.username if self.request else self.username
        )
        actions = [Action(action) for action in apply_actions]

        bk_iam_path = "/project,{}/".format(self.project_key)
        resources = [
            Resource(
                BK_IAM_SYSTEM_ID,
                "project",
                str(self.project_key),
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

    def get_page_permit(self):

        apply_actions = ["page_view"]

        subject = Subject(
            "user", self.request.user.username if self.request else self.username
        )
        actions = [Action(action) for action in apply_actions]

        data = []
        self.parse_tree(self.version.get_page_data()[0], data)
        resources = [
            [
                Resource(
                    BK_IAM_SYSTEM_ID,
                    "page",
                    str(resource["id"]),
                    {
                        "iam_resource_owner": resource.get("creator", ""),
                        "_bk_iam_path_": "/project,{}/".format(self.project_key),
                        "name": resource.get("resource_name", ""),
                    },
                )
            ]
            for resource in data
        ]
        if settings.ENVIRONMENT == "dev" or self.have_project_admin_permit():
            # dev 环境不走权限中心
            actions_result = {"page_view": True}
            auth_actions = {str(resource["id"]): actions_result for resource in data}
            return self.build_response(apply_actions[0], auth_actions=auth_actions)

        request = MultiActionRequest(BK_IAM_SYSTEM_ID, subject, actions, [], None)
        try:
            auth_actions = self._iam.batch_resource_multi_actions_allowed(
                request, resources
            )
        except BaseException:
            auth_actions = {}

        return self.build_response(apply_actions[0], auth_actions=auth_actions)

    def get_list_component_data(self, item):
        results = []
        for button_group in item["config"]["buttonGroup"]:
            if "id" not in button_group:
                continue
            results.append(
                {"id": button_group["id"], "display_name": button_group["name"]}
            )

        for option in item["config"]["optionList"]:
            if "id" not in option:
                continue
            results.append({"id": option["id"], "display_name": option["name"]})

        return results

    def get_action_permit(self, page_id):
        components = self.version.get_page_component(str(page_id))
        data = []
        for component in components:
            if component["type"] == "LIST":
                data.extend(self.get_list_component_data(component))
            if component["type"] in ["FUNCTION"]:
                data.append(
                    {
                        "id": component["id"],
                        "display_name": component["config"].get("name", ""),
                    }
                )
            if component["type"] == "SHEET":
                data.append(
                    {
                        "id": component["id"],
                        "display_name": "提交",
                    }
                )

        apply_actions = ["action_execute"]
        subject = Subject(
            "user", self.request.user.username if self.request else self.username
        )
        actions = [Action(action) for action in apply_actions]

        if settings.ENVIRONMENT == "dev" or self.have_project_admin_permit():
            # dev 环境不走权限中心
            actions_result = {"action_execute": True}
            auth_actions = {str(resource["id"]): actions_result for resource in data}
            return self.build_response(apply_actions[0], auth_actions=auth_actions)

        resources = [
            [
                Resource(
                    BK_IAM_SYSTEM_ID,
                    "action",
                    str(resource["id"]),
                    {
                        "iam_resource_owner": resource.get("creator", ""),
                        "_bk_iam_path_": "/project,{}/page,{}/".format(
                            self.project_key, page_id
                        ),
                        "name": resource.get("resource_name", ""),
                    },
                )
            ]
            for resource in data
        ]

        request = MultiActionRequest(BK_IAM_SYSTEM_ID, subject, actions, [], None)
        try:
            auth_actions = self._iam.batch_resource_multi_actions_allowed(
                request, resources
            )
        except BaseException:
            auth_actions = {}

        return self.build_response(apply_actions[0], auth_actions=auth_actions)

    def build_response(self, action, auth_actions):
        data = {}
        for resource_id, action_dict in auth_actions.items():
            data[resource_id] = action_dict.get(action, False)
        return data
