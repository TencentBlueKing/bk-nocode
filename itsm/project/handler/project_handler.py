# -*- coding: utf-8 -*-
import datetime

from django.conf import settings
from django.utils.translation import ugettext as _

from iam.api.client import Client
from common.log import logger
from itsm.component.exceptions import ProjectSettingsNotFound, ProjectNotFound
from itsm.project.handler.permit_engine_handler import PermitInitManagerDispatcher
from itsm.project.handler.service_handler import ServiceHandler
from itsm.project.models import ProjectConfig, Project
from itsm.role.models import UserRole
from itsm.service.handler.service_handler import FavouriteServiceHandler
from itsm.service.models import ServiceCatalog
from nocode.base.base_handler import APIModel
from nocode.page.handlers.page_handler import PageModelHandler
from nocode.project_manager.handlers.operate_handler import OperateLogHandler
from nocode.worksheet.handlers.project_version_handler import ProjectVersionHandler


class PageModelHandler(PageModelHandler):
    pass


class ProjectConfigHandler(APIModel):
    def __init__(self, project_key=None):
        self.project_key = project_key
        self.obj = None

        super(ProjectConfigHandler, self).__init__()

    def _get_instance(self):
        try:
            obj = ProjectConfig.objects.get(project_key=self.project_key)
        except ProjectConfig.DoesNotExist:
            raise ProjectSettingsNotFound()
        return obj

    @property
    def instance(self):
        if self.obj is None:
            self.obj = self._get_instance()
        return self.obj

    def init_project_config(self, project_key, config):
        return self.create_project_config(project_key, config)

    def create_project_config(self, project_key, config):
        return ProjectConfig.objects.create(project_key=project_key, **config)

    def get_workflow_prefix(self):
        # 从当前版本中获取流程前缀
        current_version_project = ProjectVersionHandler(
            project_key=self.project_key
        ).version
        workflow_prefix = current_version_project.project_config.get(
            "workflow_prefix", "REQ"
        )
        return workflow_prefix


class ProjectHandler(APIModel):
    def __init__(self, project_key=None, instance=None, **kwargs):
        self.project_key = project_key
        self.kwargs = kwargs
        self.obj = instance
        self.iam_client = Client(
            settings.APP_CODE,
            settings.SECRET_KEY,
            settings.BK_IAM_INNER_HOST,
            settings.BK_IAM_ESB_PAAS_HOST,
        )
        super(ProjectHandler, self).__init__()

    def _get_instance(self):
        try:
            if self.project_key is None:
                obj = Project.objects.get(**self.kwargs)
            else:
                obj = Project.objects.get(key=self.project_key)
        except Project.DoesNotExist:
            raise ProjectNotFound()
        return obj

    def get_instance(self):
        if self.obj is None:
            self.obj = self._get_instance()
        return self.obj

    def update_owner(self, username_list):
        instance = self.get_instance()
        instance.owner = {"users": username_list}
        instance.save()

    def update_data_owner(self, username_list):
        instance = self.get_instance()
        instance.data_owner = {"users": username_list}
        # 用户组不存在，不存在直接新建，通过新的用户列表重新同步
        manager = PermitInitManagerDispatcher(instance=instance)
        logger.info("变更数据管理员用户组成员， username_list = {}".format(username_list))
        manager.update_data_user_group(username_list)
        instance.save()
        logger.info("平台同步数据管理员用户组， username_list = {}".format(username_list))

    @property
    def instance(self):
        if self.obj is None:
            self.obj = self._get_instance()
        return self.obj

    @property
    def exist(self):
        return True if self.instance else False

    @property
    def all_project(self):
        return Project.objects.all()

    @property
    def get_project_owner(self):
        return self.instance.owner["users"]

    def get_manager_of_all_projects(self, queryset):
        projects = queryset.values("key", "name", "owner", "data_owner")
        manager_of_project = []
        for project in projects:
            project["owner"] = project["owner"]["users"]
            project["data_owner"] = project["data_owner"]["users"]
            manager_of_project.append(project)
        return manager_of_project

    def save(self):
        self.instance.save()

    def init_operate_catalogs(self, operate_catalogs):
        level_1 = [item for item in operate_catalogs if item["level"] == 1]
        root_key = "{}_{}".format(self.instance.key, "root")
        root = ServiceCatalog.create_root(
            key=root_key, name=_("根目录"), is_deleted=False, project_key=self.instance.key
        )
        for level1 in level_1:
            ServiceCatalog.create_catalog(
                key="{}_{}".format(self.instance.key, level1["key"]),
                name=level1["name"],
                parent=root,
                project_key=self.obj.key,
            )

    def change_project_publish_status(self, status):
        self.instance.publish_status = status
        if status == "RELEASE":
            self.instance.publish_time = datetime.datetime.now()
        self.instance.instance.save()

    def favourite_service_tree(self, username):
        """
        [
            {
                project: {
                    project_key:
                    project_name
                }
                favourite_service: [
                    {
                        id:
                        info:
                    },
                    ...
                ]
            },
            ...
        ]
        """
        projects = self.all_project
        all_favourite = FavouriteServiceHandler().get_all_service(username=username)
        tree = [
            self.get_favourite_service(project, all_favourite) for project in projects
        ]
        return tree

    def get_favourite_service(self, project, all_favourite):

        data_struct = dict()
        data_struct["project"] = {
            "project_key": project.pk,
            "name": project.name,
            "config": {
                "logo": project.logo,
                "color": project.color,
            },
        }
        data_struct["favourite_services"] = []

        service_list = (
            ServiceHandler()
            .filter(project_key=project.key)
            .values("id", "name", "desc")
        )
        service_of_project = [service.get("id") for service in service_list]
        # 项目下应用id与全部收藏的应用id取交集
        favourite_of_project = list(set(all_favourite) & set(service_of_project))
        for service_id in favourite_of_project:
            tmp = {}
            service = service_list.get(pk=service_id)
            tmp["id"] = service.get("id")
            tmp["name"] = service.get("name")
            tmp["desc"] = service.get("desc")
            data_struct["favourite_services"].append(tmp)
        return data_struct

    def init_user_group(self, username):
        # role_key name role_type access 5members desc
        # GENERAL
        UserRole.objects.create(
            name="应用管理员",
            role_key="MANAGER",
            role_type="GENERAL",
            owners=username,
            members=",{username},".format(username=username),
            project_key=self.instance.key,
            desc="具有该应用的管理权限",
        )
        # log create
        OperateLogHandler.log_create(
            content="{username}创建应用：{project}， 初始化应用管理员组".format(
                project=self.instance.name,
                username=username,
            ),
            operator=username,
            project_key=self.instance.key,
            module=self.instance.name,
        )
