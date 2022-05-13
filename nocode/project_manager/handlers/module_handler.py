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

from bkapigw.bk_iam.shortcuts import get_client_by_user
from common.log import logger
from iam.api.client import Client
from itsm.project.handler.project_handler import ProjectHandler
from itsm.project.models import ProjectConfig
from itsm.service.models import Service, PeriodicTask, WorkSheetEvent
from itsm.workflow.models import Workflow
from nocode.page.handlers.page_handler import PageModelHandler, PageComponentHandler
from nocode.permit.models import UserGroup
from nocode.project_manager.exceptions import (
    ProjectConfigDoesNotExists,
    MigrateUserGroupError,
    MigrateUserGroupPoliciesError,
    MigrateUserGroupMemberError,
)
from nocode.project_manager.models import ProjectVersion
from nocode.worksheet.handlers.worksheet_field_handler import WorkSheetFieldModelHandler
from nocode.worksheet.handlers.worksheet_handler import WorkSheetModelHandler


class BaseVersionGenerator:
    def create_version(self, project_key):
        pass


class ProjectConfigVersionGenerator(BaseVersionGenerator):
    def create_version(self, project_key):
        try:
            config = ProjectConfig.objects.get(project_key=project_key)
        except ProjectConfig.DoesNotExist:
            raise ProjectConfigDoesNotExists()

        return config.tag_data()


class PageVersionGenerator(BaseVersionGenerator):
    def create_version(self, project_key):
        tree = PageModelHandler().tree_data(project_key=project_key)
        return tree


class PageComponentVersionGenerator(BaseVersionGenerator):
    def create_version(self, project_key):
        data = {}
        page_ids = (
            PageModelHandler()
            .filter(project_key=project_key)
            .values_list("id", flat=True)
        )
        for page_id in page_ids:
            data[page_id] = self.get_page_component(page_id)

        return data

    def get_page_component(self, page_id):
        page_components = PageComponentHandler().filter(page_id=page_id)
        return [page_component.tag_data() for page_component in page_components]


class WorkSheetVersionGenerator(BaseVersionGenerator):
    def create_version(self, project_key):
        worksheets = WorkSheetModelHandler().filter(project_key=project_key)
        return [worksheet.tag_data() for worksheet in worksheets]


class WorkSheetFieldVersionGenerator(BaseVersionGenerator):
    def create_version(self, project_key):
        worksheet_ids = (
            WorkSheetModelHandler()
            .filter(project_key=project_key)
            .values_list("id", flat=True)
        )
        data = {}
        for worksheet_id in worksheet_ids:
            data[worksheet_id] = self.get_worksheet_filed(worksheet_id)

        return data

    def get_worksheet_filed(self, worksheet_id):
        worksheet_fields = WorkSheetFieldModelHandler().filter(
            worksheet_id=worksheet_id, is_deleted=False
        )
        return [worksheet_field.tag_data() for worksheet_field in worksheet_fields]


class WorkSheetEventVersionGenerator(BaseVersionGenerator):
    def create_version(self, project_key):
        worksheet_events = WorkSheetEvent.objects.filter(project_key=project_key)
        events = {}
        for item in worksheet_events:
            if item.id in events:
                events[item.id].append(item.tag_data())
            else:
                events.setdefault(item.id, [item.tag_data()])
        return events


class ProjectModuleHandler:
    def __init__(self, project_key):
        self.project_key = project_key

    @property
    def handler(self):
        return ProjectHandler(project_key=self.project_key)

    @property
    def instance(self):
        return self.handler.instance

    def update_status(self, publish_status="RELEASING"):
        project = self.handler.get_instance()
        project.publish_status = publish_status
        project.save()

    def update_version(self, version_number):
        project = self.handler.get_instance()
        project.version_number = version_number
        project.publish_status = "RELEASED"
        project.save()

    def updating(self):
        project = self.handler.get_instance()
        project.publish_status = "RELEASING"
        project.save()

    def update_failed(self):
        project = self.handler.get_instance()
        project.publish_status = "CHANGED"
        project.save()


class ServiceModuleHandler:
    def __init__(self, project_key):
        self.project_key = project_key

    def publish_periodic_task(self, service):
        service.apply_periodic_task()

    def migrate_periodic_task(self):
        PeriodicTask.migrate_periodic_task(self.project_key)

    def update_service(self):
        services = Service.objects.filter(project_key=self.project_key)
        self.migrate_periodic_task()
        for service in services:
            self.update_workflow(service=service)
            self.publish_periodic_task(service=service)

    def update_workflow(self, service):
        workflow_id = service.workflow.workflow_id
        workflow = Workflow.objects.get(id=workflow_id)
        service.workflow_id = workflow.create_version()
        service.save()

    @classmethod
    def verify(cls, service_id):
        try:
            service = Service.objects.get(id=service_id)
            if service.is_valid:
                return True
        except Service.DoesNotExist:
            return False

        return False


class WorkSheetFieldModuleHandler:
    def __init__(self, worksheet_id):
        self.worksheet_id = worksheet_id

    def fields(self):
        return WorkSheetFieldModelHandler().filter(worksheet_id=self.worksheet_id)

    def deleted_fields(self):
        return WorkSheetFieldModelHandler().get_delete_fields(
            worksheet_id=self.worksheet_id
        )


class WorkSheetModuleHandler:
    def __init__(self, project_key):
        self.project_key = project_key

    def ids(self):
        return (
            WorkSheetModelHandler()
            .filter(project_key=self.project_key)
            .values_list("id", flat=True)
        )

    def deleted_worksheets(self):
        return WorkSheetModelHandler().delete_worksheets(self.project_key)


class PageHandler:
    def filter_permit_tree(self, username, tree):
        return PageModelHandler().filter_permit_tree(username=username, node=tree)

    def get_page_type(self, page_id):
        return PageModelHandler(page_id=page_id).instance.type


class UserGroupHandlerOpen:
    def __init__(self, project_key):
        self.project_key = project_key
        self.iam_client = Client(
            settings.APP_CODE,
            settings.SECRET_KEY,
            settings.BK_IAM_INNER_HOST,
            settings.BK_IAM_ESB_PAAS_HOST,
        )
        self.project = ProjectHandler(self.project_key).instance

    def build_page_path(self, configs):
        paths = []
        for item in configs.get("page_view", []):
            paths.append(
                [
                    {
                        "system": "bk_nocode",
                        "type": "project",
                        "id": self.project.key,
                        "name": self.project.name,
                    },
                    {
                        "system": "bk_nocode",
                        "type": "page",
                        "id": item["id"],
                        "name": item["name"],
                    },
                ]
            )
        return paths

    def build_action_path(self, configs):
        paths = []
        for item in configs.get("action_execute", []):
            for action in item["actions"]:
                paths.append(
                    [
                        {
                            "system": settings.BK_IAM_SYSTEM_ID,
                            "type": "project",
                            "id": self.project.key,
                            "name": self.project.name,
                        },
                        {
                            "system": settings.BK_IAM_SYSTEM_ID,
                            "type": "page",
                            "id": item["id"],
                            "name": item["name"],
                        },
                        {
                            "system": settings.BK_IAM_SYSTEM_ID,
                            "type": "action",
                            "id": action["id"],
                            "name": action["name"],
                        },
                    ]
                )
        return paths

    def build_request_policies(self, configs):
        """
        动态构建用户的policies
        """
        action_paths = self.build_action_path(configs)

        page_paths = self.build_page_path(configs)

        page_data = {
            "system": "bk_nocode",
            "actions": [{"id": "page_view"}],
            "resources": [{"system": "bk_nocode", "type": "page", "paths": page_paths}],
        }

        action_data = {
            "system": "bk_nocode",
            "actions": [{"id": "action_execute"}],
            "resources": [
                {"system": "bk_nocode", "type": "action", "paths": action_paths}
            ],
        }

        return action_data, page_data

    def create_new_group(self, user_group):

        logger.info(
            "[UserGroupHandler][create_new_group] 开始创建新的用户组，user_group = {}".format(
                user_group.id
            )
        )
        create_user_group_data = {
            "groups": [
                {
                    "name": user_group.name,
                    "description": "这是一段关于{}用户组的默认描述".format(user_group.name),
                }
            ]
        }
        logger.info(
            "[UserGroupHandler][create_new_group] 开始创建新的用户组，create_user_group_data = {}".format(
                create_user_group_data
            )
        )
        result, message, data = self.iam_client.create_user_group(
            grade_manager_id=self.project.rating_manager_id,
            bk_username="admin",
            bk_token="",
            data=create_user_group_data,
        )

        if not result:
            logger.info(
                "[UserGroupHandler][create_new_group] 用户组创建失败，create_user_group_data = {} "
                "error_message={}".format(create_user_group_data, message)
            )
            raise MigrateUserGroupError()

        user_group.group_id = data[0]
        user_group.save()

        logger.info(
            "[UserGroupHandler][create_new_group] 用户组创建成功，group_id = {}".format(data[0])
        )

        action_policies, page_actions = self.build_request_policies(
            user_group.action_configs
        )

        logger.info(
            "[UserGroupHandler][create_new_group] 开始更新用户组策略，action_policies = {},page_actions={}".format(
                action_policies, page_actions
            )
        )

        if action_policies["resources"][0].get("paths", []):
            result, message, data = self.iam_client.create_user_group_policies(
                user_group_id=user_group.group_id,
                bk_token="",
                bk_username="admin",
                data=action_policies,
            )
            if not result:
                logger.info(
                    "[UserGroupHandler][create_new_group] 用户组操作策略更新失败，action_policies = {},"
                    "page_actions={}, error={}".format(
                        action_policies, page_actions, message
                    )
                )
                raise MigrateUserGroupPoliciesError("用户组操作策略更新失败")

        if page_actions["resources"][0].get("paths", []):
            result, message, data = self.iam_client.create_user_group_policies(
                user_group_id=user_group.group_id,
                bk_token="",
                bk_username="admin",
                data=page_actions,
            )
            if not result:
                logger.info(
                    "[UserGroupHandler][create_new_group] 用户组操作策略更新失败，action_policies = {},"
                    "page_actions={}, error={}".format(
                        action_policies, page_actions, message
                    )
                )
                raise MigrateUserGroupPoliciesError("用户组页面访问策略更新失败")

        members = []
        for user in user_group.users.get("members", []):
            members.append({"type": "user", "id": user})

        for department_id in user_group.users.get("departments", []):
            members.append({"type": "department", "id": department_id})

        if not members:
            logger.info("[UserGroupHandler][create_new_group] 监测到用户组没有配置人员信息，跳过初始化人员")
            return

        result, message = self.iam_client.add_user_group_members(
            group_id=user_group.group_id,
            bk_token="",
            bk_username="admin",
            data={"members": members, "expired_at": 4102444800},
        )

        if not result:
            raise MigrateUserGroupMemberError("用户组人员添加失败， message={}".format(message))

    def delete_group(self):
        deleted_groups = UserGroup._objects.filter(
            project_key=self.project_key, is_deleted=True
        )

        for deleted_group in deleted_groups:
            self.iam_client.delete_user_group(
                group_id=deleted_group.group_id,
                bk_token="",
                bk_username="admin",
                data={},
            )

    def publish(self):

        self.delete_group()

        user_groups = UserGroup.objects.filter(project_key=self.project_key)
        for user_group in user_groups:
            # 如果用户组没有ID, 证明用户组是没有初始化过的，需要新建
            if user_group.group_id == 0:
                # create_new_user_group
                self.create_new_group(user_group)
            else:
                result, message, data = self.iam_client.delete_user_group(
                    group_id=user_group.group_id,
                    bk_token="",
                    bk_username="admin",
                    data={},
                )
                if not result:
                    logger.info(
                        "用户组删除失败， group_id={}, user_group_id={}, error_message={}".format(
                            user_group.group_id, user_group.id, message
                        )
                    )
                    user_group.group_id = 0
                    user_group.save()
                self.create_new_group(user_group)


class UserGroupHandlerIeod(UserGroupHandlerOpen):
    def __init__(self, project_key):
        self.project_key = project_key
        if settings.RUN_MODE == "STAGING":
            self.client = get_client_by_user("admin", stage="stage")
        else:
            self.client = get_client_by_user("admin")
        self.project = ProjectHandler(self.project_key).instance

    def create_new_group(self, user_group):

        logger.info(
            "[UserGroupHandler][create_new_group] 开始创建新的用户组，user_group = {}".format(
                user_group.id
            )
        )
        create_user_group_data = {
            "groups": [
                {
                    "name": user_group.name,
                    "description": "这是一段关于{}用户组的默认描述".format(user_group.name),
                }
            ]
        }
        logger.info(
            "[UserGroupHandler][create_new_group] 开始创建新的用户组，create_user_group_data = {}".format(
                create_user_group_data
            )
        )

        data = self.client.iam.create_user_group(
            path_params={"id": self.project.rating_manager_id},
            params=create_user_group_data,
        )

        if not data["result"]:
            logger.info(
                "[UserGroupHandler][create_new_group] 用户组创建失败，create_user_group_data = {} "
                "error_message={}".format(create_user_group_data, data["message"])
            )
            raise MigrateUserGroupError()

        user_group.group_id = data["data"][0]
        user_group.save()

        logger.info(
            "[UserGroupHandler][create_new_group] 用户组创建成功，group_id = {}".format(
                data["data"][0]
            )
        )

        action_policies, page_actions = self.build_request_policies(
            user_group.action_configs
        )

        logger.info(
            "[UserGroupHandler][create_new_group] 开始更新用户组策略，action_policies = {},page_actions={}".format(
                action_policies, page_actions
            )
        )

        if action_policies["resources"][0].get("paths", []):

            data = self.client.iam.create_user_group_policies(
                path_params={"id": user_group.group_id}, params=action_policies
            )

            if not data["result"]:
                logger.info(
                    "[UserGroupHandler][create_new_group] 用户组操作策略更新失败，action_policies = {},"
                    "page_actions={}, error={}".format(
                        action_policies, page_actions, data["message"]
                    )
                )
                raise MigrateUserGroupPoliciesError("用户组操作策略更新失败")

        if page_actions["resources"][0].get("paths", []):
            data = self.client.iam.create_user_group_policies(
                path_params={"id": user_group.group_id}, params=page_actions
            )
            if not data["result"]:
                logger.info(
                    "[UserGroupHandler][create_new_group] 用户组操作策略更新失败，action_policies = {},"
                    "page_actions={}, error={}".format(
                        action_policies, page_actions, data["message"]
                    )
                )
                raise MigrateUserGroupPoliciesError("用户组页面访问策略更新失败")

        members = []
        for user in user_group.users.get("members", []):
            members.append({"type": "user", "id": user})

        for department_id in user_group.users.get("departments", []):
            members.append({"type": "department", "id": department_id})

        if not members:
            logger.info("[UserGroupHandler][create_new_group] 监测到用户组没有配置人员信息，跳过初始化人员")
            return

        data = self.client.iam.add_user_group_members(
            path_params={"id": user_group.group_id},
            params={"members": members, "expired_at": 4102444800},
        )

        if not data["result"]:
            raise MigrateUserGroupMemberError(
                "用户组人员添加失败， message={}".format(data["message"])
            )

    def delete_group(self):
        deleted_groups = UserGroup._objects.filter(
            project_key=self.project_key, is_deleted=True
        )

        for deleted_group in deleted_groups:
            self.client.iam.delete_user_group(
                path_params={"id": deleted_group.group_id}
            )

    def publish(self):

        self.delete_group()

        user_groups = UserGroup.objects.filter(project_key=self.project_key)
        for user_group in user_groups:
            # 如果用户组没有ID, 证明用户组是没有初始化过的，需要新建
            if user_group.group_id == 0:
                # create_new_user_group
                self.create_new_group(user_group)
            else:
                data = self.client.iam.delete_user_group(
                    path_params={"id": user_group.group_id}
                )
                if not data["result"]:
                    logger.info(
                        "用户组删除失败， group_id={}, user_group_id={}, error_message={}".format(
                            user_group.group_id, user_group.id, data["message"]
                        )
                    )
                    user_group.group_id = 0
                    user_group.save()
                self.create_new_group(user_group)


class UserGroupHandlerDispatcher:
    def __init__(self, project_key):
        self.project_key = project_key

    def publish(self):
        if settings.RUN_VER == "ieod":
            UserGroupHandlerIeod(project_key=self.project_key).publish()
        else:
            UserGroupHandlerOpen(project_key=self.project_key).publish()


class ProjectVersionHandler:
    def __init__(self, project_key, version_number):
        self.project_key = project_key
        self.version_number = version_number

    def get_version_page_components(self):
        return ProjectVersion.objects.get(
            project_key=self.project_key, version_number=self.version_number
        ).page_component
