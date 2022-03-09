# -*- coding: utf-8 -*-
from django.conf import settings

from bkapigw.bk_iam.shortcuts import get_client_by_user
from common.log import logger
from iam.api.client import Client
from itsm.component.constants import ADMIN
from itsm.component.utils.basic import dotted_name
from itsm.component.utils.client_backend_query import get_list_departments
from itsm.project.execptions import (
    InitGradeManagerError,
    InitUserGroupError,
    InitUserGroupPolicesError,
    InitUserGroupMembersError,
    GetUserGroupMembersError,
    GetUserGroupError,
    DeleteUserGroupMembersError,
)


class BasePermitInitManager:
    def __init__(self, instance):
        self.instance = instance

    def init_grade_managers(self):
        pass

    def init_data_user_group(self):
        pass

    def update_data_user_group(self, username_list):
        pass

    def get_departments_id(self):
        res = get_list_departments({"fields": "id"})
        return res[0]["id"]

    def build_grade_manager_data(self):
        GRANT_DEPARTMENT_ID = settings.GRANT_DEPARTMENT_ID

        if GRANT_DEPARTMENT_ID is None:
            department_id = self.get_departments_id()
        else:
            department_id = int(GRANT_DEPARTMENT_ID)

        # 后续可以做成mako渲染
        request_data = {
            "system": settings.BK_IAM_SYSTEM_ID,
            "name": "{}-分级管理员".format(self.instance.name),
            "description": "",
            "members": [self.instance.creator],
            "authorization_scopes": [
                {
                    "system": settings.BK_IAM_SYSTEM_ID,
                    "actions": [{"id": "action_execute"}],
                    "resources": [
                        {
                            "system": settings.BK_IAM_SYSTEM_ID,
                            "type": "action",
                            "paths": [
                                [
                                    {
                                        "system": settings.BK_IAM_SYSTEM_ID,
                                        "type": "project",
                                        "id": self.instance.key,
                                        "name": self.instance.name,
                                    }
                                ]
                            ],
                        }
                    ],
                },
                {
                    "system": settings.BK_IAM_SYSTEM_ID,
                    "actions": [{"id": "page_view"}],
                    "resources": [
                        {
                            "system": settings.BK_IAM_SYSTEM_ID,
                            "type": "page",
                            "paths": [
                                [
                                    {
                                        "system": settings.BK_IAM_SYSTEM_ID,
                                        "type": "project",
                                        "id": self.instance.key,
                                        "name": self.instance.name,
                                    }
                                ]
                            ],
                        }
                    ],
                },
                {
                    "system": settings.BK_IAM_SYSTEM_ID,
                    "actions": [{"id": "project_admin"}],
                    "resources": [
                        {
                            "system": settings.BK_IAM_SYSTEM_ID,
                            "type": "project",
                            "paths": [
                                [
                                    {
                                        "system": settings.BK_IAM_SYSTEM_ID,
                                        "type": "project",
                                        "id": self.instance.key,
                                        "name": self.instance.name,
                                    }
                                ]
                            ],
                        }
                    ],
                },
            ],
            "subject_scopes": [{"type": "department", "id": department_id}],
        }
        return request_data

    def build_create_user_group_data(self):
        name = "{}-管理员".format(self.instance.name)
        request_data = {
            "groups": [{"name": name, "description": "这是一段关于{}的默认描述".format(name)}]
        }
        return request_data

    def build_data_user_group_data(self):
        """
        数据管理员组数据构建
        """
        name = "{}-数据管理员".format(self.instance.name)
        request_data = {
            "groups": [{"name": name, "description": "这是一段关于{}数据管理员的默认描述".format(name)}]
        }
        return request_data

    def build_user_group_policies(self):
        request_data = {
            "system": settings.BK_IAM_SYSTEM_ID,
            "actions": [{"id": "project_admin"}],
            "resources": [
                {
                    "system": settings.BK_IAM_SYSTEM_ID,
                    "type": "project",
                    "paths": [
                        [
                            {
                                "system": settings.BK_IAM_SYSTEM_ID,
                                "type": "project",
                                "id": self.instance.key,
                                "name": self.instance.name,
                            }
                        ]
                    ],
                }
            ],
        }
        return request_data


class PermitInitManagerOpen(BasePermitInitManager):
    def __init__(self, instance):
        self.instance = instance
        self.iam_client = Client(
            settings.APP_CODE,
            settings.SECRET_KEY,
            settings.BK_IAM_INNER_HOST,
            settings.BK_IAM_ESB_PAAS_HOST,
        )

    def init_grade_managers(self):
        request_data = self.build_grade_manager_data()
        result, message, data = self.iam_client.grade_managers(
            bk_token="", bk_username="admin", data=request_data
        )

        if not result:
            raise InitGradeManagerError("分级管理员创建失败，调用权限中心报错:error={}".format(message))

        self.instance.rating_manager_id = data["id"]
        self.instance.save()

        # 开始创建管理员用户组
        self.create_admin_user_group(data["id"])

        # 开始创建数据管理员用户组
        self.create_data_user_group(data["id"])

    def create_admin_user_group(self, rating_manager_id):
        """
        管理员用户组创建
        """
        request_data = self.build_create_user_group_data()
        result, message, data = self.iam_client.create_user_group(
            rating_manager_id,
            bk_token="",
            bk_username="admin",
            data=request_data,
        )
        if not result:
            logger.info(
                "用户组创建失败，request_data = {}, message={}".format(request_data, message)
            )
            raise InitUserGroupError("用户组创建失败，调用权限中心报错： message={}".format(message))

        user_group_id = data[0]
        logger.info("管理员用户组创建成功， user_group_id = {}".format(user_group_id))
        self.create_user_group_policies(user_group_id)
        self.add_user_group_members(user_group_id)

    def create_user_group_policies(self, user_group_id):
        """
        用户组策略
        """
        request_data = self.build_user_group_policies()
        result, message, data = self.iam_client.create_user_group_policies(
            user_group_id=user_group_id,
            bk_token="",
            bk_username="admin",
            data=request_data,
        )
        if not result:
            logger.info("用户组策略创建失败，request_data = {}".format(request_data))
            raise InitUserGroupPolicesError("用户组策略创建失败, 调用权限中心报错:{}".format(message))

    def add_user_group_members(self, user_group_id):
        """
        用户组添加人员, 未来这里可能会是项目负责人
        """
        # 如果admin创建的应用，跳过用户组加人的环节
        if self.instance.creator == "admin":
            return

        members = [{"type": "user", "id": self.instance.creator}]
        result, message = self.iam_client.add_user_group_members(
            group_id=user_group_id,
            bk_token="",
            bk_username="admin",
            data={"members": members, "expired_at": 4102444800},
        )
        if not result:
            logger.info(
                "用户组人员添加失败 request_data = {}, message={}".format(members, message)
            )
            raise InitUserGroupMembersError()

    def create_data_user_group(self, rating_manager_id):
        """
        数据管理员用户组创建
        """
        request_data = self.build_data_user_group_data()
        result, message, data = self.iam_client.create_user_group(
            rating_manager_id,
            bk_token="",
            bk_username="admin",
            data=request_data,
        )
        if not result:
            logger.info(
                "数据管理员用户组创建失败，request_data = {}, message={}".format(
                    request_data, message
                )
            )
            raise InitUserGroupError(
                "数据管理员用户组创建失败，调用权限中心报错： message={}".format(message)
            )
        user_group_id = data[0]
        logger.info("数据管理员用户组创建成功， user_group_id = {}".format(user_group_id))
        # project 保存数据管理用户组id
        self.instance.user_group_id = user_group_id
        self.create_data_user_group_policies(user_group_id)
        self.instance.save()

    def create_data_user_group_policies(self, user_group_id):
        """
        数据管理员组策略构建
        """
        request_data = self.build_user_group_policies()
        result, message, data = self.iam_client.create_user_group_policies(
            user_group_id=user_group_id,
            bk_token="",
            bk_username="admin",
            data=request_data,
        )
        if not result:
            logger.info("数据管理员用户组策略创建失败，request_data = {}".format(request_data))
            raise InitUserGroupPolicesError(
                "数据管理员用户组策略创建失败, 调用权限中心报错:{}".format(message)
            )

    def get_user_group_members(self):
        result, message, data = self.iam_client.get_user_group_members(
            group_id=self.instance.user_group_id,
            bk_token="",
            bk_username="admin",
        )
        if not result:
            logger.info("数据管理员用户组成员获取失败, message={}".format(message))
            raise GetUserGroupMembersError(
                "数据管理员获取用户组人员失败，调用权限中心报错： message={}".format(message)
            )
        return data["results"]

    def user_group_exist(self):
        result, message, data = self.iam_client.get_user_group(
            grade_manager_id=self.instance.rating_manager_id,
            bk_token="",
            bk_username="admin",
        )
        exit_flag = None
        if not result:
            logger.info("数据管理员用户组获取失败, message={}".format(message))
            raise GetUserGroupError("数据管理员获取用户组失败，调用权限中心报错： message={}".format(message))
        for item in data["results"]:
            if item["id"] == self.instance.user_group_id:
                exit_flag = True
                break
        return exit_flag

    def add_data_user_group_members(self, user_group_id, members):
        """
        数据用户组添加人员,
        """

        result, message = self.iam_client.add_user_group_members(
            group_id=user_group_id,
            bk_token="",
            bk_username="admin",
            data={"members": members, "expired_at": 4102444800},
        )

        if not result:
            logger.info(
                "用户组人员添加失败 request_data = {}, message={}".format(members, message)
            )
            raise InitUserGroupMembersError()

    def delete_data_user_group_members(self, user_group_id, data):
        """
        数据用户组移除人员,
        """

        result, message = self.iam_client.delete_user_group_members(
            group_id=user_group_id,
            bk_token="",
            bk_username="admin",
            data=data,
        )

        if not result:
            logger.error(
                "用户组人员移除失败 request_data = {}, message={}".format(data, message)
            )
            raise DeleteUserGroupMembersError()

    def recreate_data_user_group(self, username_set):
        logger.info("数据管理员用户组重新同步")
        username_struct = [{"id": user, "type": "user"} for user in username_set]
        # 重新同步用戶組
        self.create_data_user_group(self.instance.rating_manager_id)
        self.add_data_user_group_members(self.instance.user_group_id, username_struct)
        logger.info("数据管理员用户组添加管理员成功， username_list = {}".format(username_set))

    def synchronize_data_user_group(self, username_set):
        # 同步到权限中心
        # 获取当前用户组成员
        current_username_set = set()
        for item in self.get_user_group_members():
            current_username_set.add(item["id"])
        # 初始无成员
        if not current_username_set:
            username_struct = [{"id": user, "type": "user"} for user in username_set]
            self.add_data_user_group_members(
                self.instance.user_group_id, username_struct
            )
            self.instance.save()
            return
        logger.info("当前数据管理员， username_list = {}".format(current_username_set))
        remove_user = current_username_set - username_set
        logger.info("删除数据管理员， remove_user = {}".format(remove_user))
        add_user = username_set - current_username_set
        logger.info("添加数据管理员， add_user = {}".format(add_user))
        # 删除用户组成员
        if remove_user:
            logger.info("数据管理员用户组移除管理员， username_list = {}".format(remove_user))
            remove_struct = ""
            for user in remove_user:
                remove_struct += dotted_name(user, mode="suffix")
            remove_struct_data = {"ids": remove_struct, "type": "user"}
            self.delete_data_user_group_members(
                self.instance.user_group_id, remove_struct_data
            )
        # 添加用户组成员
        if add_user:
            logger.info("数据管理员用户组新增管理员， username_list = {}".format(add_user))
            add_struct = [{"id": user, "type": "user"} for user in add_user]
            self.add_data_user_group_members(self.instance.user_group_id, add_struct)

    def update_data_user_group(self, username_list):
        exit_flag = self.user_group_exist()
        username_set = set(username_list)
        # todo 屏蔽超管类型用户
        # 获取超管用户
        username_set.discard(ADMIN)
        logger.info("数据管理员用户组添加管理员， username_list = {}".format(username_list))
        if not exit_flag:
            if username_set:
                self.recreate_data_user_group(username_set)
        else:
            self.synchronize_data_user_group(username_set)

    def init_data_user_group(self):
        return self.create_data_user_group(self.instance.rating_manager_id)


class PermitInitManagerIeod(BasePermitInitManager):
    def __init__(self, instance):
        self.instance = instance
        if settings.RUN_MODE == "STAGING":
            self.client = get_client_by_user("admin", stage="stage")
        else:
            self.client = get_client_by_user("admin")

    def init_grade_managers(self):
        request_data = self.build_grade_manager_data()
        data = self.client.iam.grade_managers(params=request_data)

        if not data["result"]:
            raise InitGradeManagerError(
                "分级管理员创建失败，调用权限中心报错:error={}".format(data["message"])
            )

        rating_manager_id = data["data"]["id"]
        self.instance.rating_manager_id = rating_manager_id
        self.instance.save()

        # 开始创建管理员用户组
        self.create_admin_user_group(rating_manager_id)

    def create_admin_user_group(self, rating_manager_id):
        """
        管理员用户组创建
        """
        request_data = self.build_create_user_group_data()
        data = self.client.iam.create_user_group(
            path_params={"id": rating_manager_id}, params=request_data
        )
        if not data["result"]:
            logger.info(
                "用户组创建失败，request_data = {}, message={}".format(
                    request_data, data["message"]
                )
            )
            raise InitUserGroupError(
                "用户组创建失败，调用权限中心报错： message={}".format(data["message"])
            )

        user_group_id = data["data"][0]
        logger.info("管理员用户组创建成功， user_group_id = {}".format(user_group_id))
        self.create_user_group_policies(user_group_id)
        self.add_user_group_members(user_group_id)

    def create_user_group_policies(self, user_group_id):
        """
        用户组策略
        """
        request_data = self.build_user_group_policies()

        data = self.client.iam.create_user_group_policies(
            path_params={"id": user_group_id}, params=request_data
        )

        if not data["result"]:
            logger.info("用户组策略创建失败，request_data = {}".format(request_data))
            raise InitUserGroupPolicesError(
                "用户组策略创建失败, 调用权限中心报错:{}".format(data["message"])
            )

    def add_user_group_members(self, user_group_id):
        """
        用户组添加人员, 未来这里可能会是项目负责人
        """
        # 如果admin创建的应用，跳过用户组加人的环节
        if self.instance.creator == "admin":
            return

        members = [{"type": "user", "id": self.instance.creator}]

        data = self.client.iam.add_user_group_members(
            path_params={"id": user_group_id},
            params={"members": members, "expired_at": 4102444800},
        )

        if not data["result"]:
            logger.info(
                "用户组人员添加失败 request_data = {}, message={}".format(
                    members, data["message"]
                )
            )
            raise InitUserGroupMembersError()

    def create_data_user_group(self, rating_manager_id):
        """
        管理员用户组创建
        """
        request_data = self.build_data_user_group_data()
        data = self.client.iam.create_user_group(
            path_params={"id": rating_manager_id}, params=request_data
        )
        if not data["result"]:
            logger.info(
                "用户组创建失败，request_data = {}, message={}".format(
                    request_data, data["message"]
                )
            )
            raise InitUserGroupError(
                "用户组创建失败，调用权限中心报错： message={}".format(data["message"])
            )

        user_group_id = data["data"][0]
        logger.info("数据管理员用户组创建成功， user_group_id = {}".format(user_group_id))
        # project 保存数据管理用户组id
        self.instance.user_group_id = user_group_id
        self.create_data_user_group_policies(user_group_id)
        self.instance.save()

    def create_data_user_group_policies(self, user_group_id):
        """
        数据管理员组策略构建
        """
        request_data = self.build_user_group_policies()
        data = self.client.iam.create_user_group_policies(
            path_params={"id": user_group_id}, params=request_data
        )

        if not data["result"]:
            logger.info("用户组策略创建失败，request_data = {}".format(request_data))
            raise InitUserGroupPolicesError(
                "用户组策略创建失败, 调用权限中心报错:{}".format(data["message"])
            )

    def get_user_group_members(self):
        data = self.client.iam.get_user_group_members(
            path_params={"id": self.instance.user_group_id}
        )
        if not data["result"]:
            logger.info("用户组成员获取失败, message={}".format(data["message"]))
            raise GetUserGroupMembersError(
                "获取用户组人员失败，调用权限中心报错： message={}".format(data["message"])
            )
        return data["data"]["results"]

    def user_group_exist(self):
        data = self.client.iam.get_user_group(
            path_params={"id": self.instance.rating_manager_id}
        )
        exit_flag = None
        if not data["result"]:
            logger.info("数据管理员用户组获取失败, message={}".format(data["message"]))
            raise GetUserGroupError(
                "获取数据管理员用户组失败，调用权限中心报错： message={}".format(data["message"])
            )
        for item in data["data"].get("results", []):
            if item["id"] == self.instance.user_group_id:
                exit_flag = True
                break
        return exit_flag

    def add_data_user_group_members(self, user_group_id, members):
        """
        数据管理员用户组添加人员,
        """

        data = self.client.iam.add_user_group_members(
            path_params={"id": user_group_id},
            params={"members": members, "expired_at": 4102444800},
        )

        if not data["result"]:
            logger.info(
                "用户组人员添加失败 request_data = {}, message={}".format(
                    members, data["message"]
                )
            )
            raise InitUserGroupMembersError()
        logger.info(
            "数据管理员用户组人员添加成功 request_data = {}, message={}".format(
                members, data["message"]
            )
        )

    def delete_data_user_group_members(self, user_group_id, members):
        """
        数据用户组移除人员,
        """

        data = self.client.iam.delete_user_group_members(
            path_params={"id": user_group_id, "type": "user", "ids": members["ids"]}
        )

        if not data["result"]:
            logger.error(
                "用户组人员移除失败 request_data = {}, message={}".format(
                    members, data["message"]
                )
            )
            raise DeleteUserGroupMembersError()
        logger.info(
            "用户组人员移除成功 request_data = {}, message={}".format(members, data["message"])
        )

    def recreate_data_user_group(self, username_set):
        logger.info("数据管理员用户组重新同步")
        username_struct = [{"id": user, "type": "user"} for user in username_set]
        # 重新同步用戶組
        self.create_data_user_group(self.instance.rating_manager_id)
        self.add_data_user_group_members(self.instance.user_group_id, username_struct)
        logger.info("数据管理员用户组添加管理员成功， username_list = {}".format(username_set))

    def synchronize_data_user_group(self, username_set):
        # 同步到权限中心
        # 获取当前用户组成员
        current_username_set = set()
        for item in self.get_user_group_members():
            current_username_set.add(item["id"])
        logger.info("数据管理员用户组当前用户有， username_list = {}".format(current_username_set))
        # 初始无成员
        if not current_username_set:
            username_struct = [{"id": user, "type": "user"} for user in username_set]
            self.add_data_user_group_members(
                self.instance.user_group_id, username_struct
            )
            self.instance.save()
            logger.info("数据管理员用户组添加管理员成功， username_list = {}".format(username_set))
            return

        remove_user = current_username_set - username_set
        logger.info("删除管理员， username_list = {}".format(remove_user))
        add_user = username_set - current_username_set
        logger.info("添加管理员， username_list = {}".format(add_user))

        # 删除用户组成员
        if remove_user:
            logger.info("数据管理员用户组移除管理员， username_list = {}".format(remove_user))
            remove_struct = ""
            for user in remove_user:
                remove_struct += dotted_name(user, mode="suffix")
            remove_data = {"type": "user", "ids": remove_struct}
            self.delete_data_user_group_members(
                self.instance.user_group_id, remove_data
            )
        # 添加用户组成员
        if add_user:
            logger.info("数据管理员用户组新增管理员， username_list = {}".format(add_user))
            add_struct = [{"id": user, "type": "user"} for user in add_user]
            self.add_data_user_group_members(self.instance.user_group_id, add_struct)

    def update_data_user_group(self, username_list):
        exit_flag = self.user_group_exist()
        username_set = set(username_list)
        # todo 屏蔽超管类型用户
        # 获取超管用户
        username_set.discard(ADMIN)
        logger.info("数据管理员用户组添加管理员， username_list = {}".format(username_list))
        if not exit_flag:
            # 避免用户组成员传空报错
            if username_set:
                self.recreate_data_user_group(username_set)
        else:
            self.synchronize_data_user_group(username_set)

    def init_data_user_group(self):
        return self.create_data_user_group(self.instance.rating_manager_id)


class PermitInitManagerDispatcher:
    def __init__(self, instance):
        self.instance = instance

    def init_permit(self):
        if settings.RUN_VER == "ieod":
            PermitInitManagerIeod(instance=self.instance).init_grade_managers()
        else:
            PermitInitManagerOpen(instance=self.instance).init_grade_managers()

    def init_data_user_group(self):
        if settings.RUN_VER == "ieod":
            PermitInitManagerIeod(instance=self.instance).init_data_user_group()
        else:
            PermitInitManagerOpen(instance=self.instance).init_data_user_group()

    def update_data_user_group(self, username_list):
        if settings.RUN_VER == "ieod":
            PermitInitManagerIeod(instance=self.instance).update_data_user_group(
                username_list
            )
        else:
            PermitInitManagerOpen(instance=self.instance).update_data_user_group(
                username_list
            )
