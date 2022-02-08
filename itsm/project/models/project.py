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
from django.db import models, transaction

from itsm.component.constants import (
    LEN_MIDDLE,
    LEN_LONG,
    EMPTY_STRING,
    LEN_NORMAL,
    LEN_SHORT,
    PUBLIC_PROJECT_PROJECT_KEY,
    EMPTY_DICT,
)
from itsm.iadmin.contants import PROJECT_SETTING
from itsm.project.models.base import Model
from django.utils.translation import ugettext as _

from itsm.service.models import ServiceCatalog
from itsm.sla.models import Sla, Schedule


class Project(Model):

    FIELDS = ("creator", "create_at", "updated_by", "update_at", "version_number")

    PUBLISH_STATUS = [
        ("RELEASED", "已发布"),
        ("UNRELEASED", "未发布"),
        ("CHANGED", "已变更未发布"),
        ("RELEASING", "发布中"),
    ]
    key = models.CharField(
        _("项目唯一标识"),
        max_length=LEN_SHORT,
        primary_key=True,
        error_messages={"unique": "该应用标识已被使用，请更换"},
    )
    name = models.CharField(_("项目名"), max_length=LEN_MIDDLE)
    desc = models.CharField(
        _("项目描述"), max_length=LEN_LONG, null=True, blank=True, default=EMPTY_STRING
    )
    logo = models.TextField(_("logo base64 内容"), default="", blank=True)
    color = models.CharField(_("项目颜色"), null=True, default="", max_length=LEN_SHORT)
    is_enabled = models.BooleanField(_("是否启用"), default=True, db_index=True)
    is_deleted = models.BooleanField(_("是否软删除"), default=False, db_index=True)
    version_number = models.CharField(
        _("当前绑定项目版本"), max_length=LEN_NORMAL, default=EMPTY_STRING
    )
    publish_time = models.DateTimeField(_("发布时间时间"), null=True)
    publish_status = models.CharField(
        _("项目状态"),
        choices=PUBLISH_STATUS,
        default="UNRELEASED",
        db_index=True,
        max_length=LEN_SHORT,
    )

    owner = models.JSONField(_("负责人"), max_length=LEN_NORMAL, default=EMPTY_DICT)
    app_code = models.CharField(default=EMPTY_STRING, max_length=LEN_NORMAL)
    app_secret = models.CharField(default=EMPTY_STRING, max_length=LEN_NORMAL)
    rating_manager_id = models.IntegerField(_("分级管理员id"), default=0)
    user_group_id = models.IntegerField(_("数据管理用户组id"), default=0)
    data_owner = models.JSONField(
        _("数据管理用户组成员"), max_length=LEN_NORMAL, default=EMPTY_DICT
    )

    resource_operations = ["project_admin"]

    def init_service_catalogs(self, catalog):
        level_1 = [item for item in catalog if item["level"] == 1]
        level_2 = [item for item in catalog if item["level"] == 2]
        # 预留支持3级
        level_3 = [item for item in catalog if item["level"] == 3]
        root_key = "{}_{}".format(self.key, "root")
        root = ServiceCatalog.create_root(
            key=root_key, name=_("根目录"), is_deleted=False, project_key=self.key
        )
        for level1 in level_1:
            l_1 = ServiceCatalog.create_catalog(
                key=level1["key"],
                name=level1["name"],
                parent=root,
                project_key=self.key,
            )
            for level2 in level_2:
                if l_1.key == level2["parent_key"]:
                    l_2 = ServiceCatalog.create_catalog(
                        key=level2["key"],
                        name=level2["name"],
                        parent=l_1,
                        project_key=self.key,
                    )
                    for level3 in level_3:
                        if l_2.key == level3["parent_key"]:
                            ServiceCatalog.create_catalog(
                                key=level3["key"],
                                name=level3["name"],
                                parent=l_2,
                                project_key=self.key,
                            )

    def init_project_settings(self):
        for project_setting in PROJECT_SETTING:
            ProjectSettings.objects.get_or_create(
                type=project_setting[1],
                key=project_setting[0],
                value=project_setting[2],
                project=self,
            )

    def init_project_sla(self):
        Sla.init_sla(Schedule.init_schedule(project_key=self.key), project_key=self.key)

    def delete(self, using=None):
        self.is_deleted = True
        self.save()

    @classmethod
    def init_default_project(cls):
        try:
            Project.objects.get_or_create(
                key=0, name="默认项目", desc="全局默认项目", creator="admin"
            )
            Project.objects.get_or_create(
                key=PUBLIC_PROJECT_PROJECT_KEY,
                name="公共项目",
                desc="全局公共项目，用于存放公共字段",
                creator="admin",
            )
        except BaseException as error:
            print("init_default_project error， error is {}".format(error))

    def tag_data(self):
        return {
            "key": self.key,
            "name": self.name,
            "desc": self.desc,
            "logo": self.logo,
            "color": self.color,
        }


class ProjectSettings(Model):
    type = models.CharField(_("类型"), max_length=LEN_NORMAL, default="FUNCTION")
    key = models.CharField(_("关键字唯一标识"), max_length=LEN_NORMAL, unique=False)
    value = models.TextField(_("系统设置值"), default=EMPTY_STRING, null=True, blank=True)
    project = models.ForeignKey("Project", help_text=_("项目"), on_delete=models.CASCADE)


class UserProjectAccessRecord(Model):
    username = models.CharField(_("用户名"), max_length=LEN_SHORT, primary_key=True)
    project_key = models.CharField(
        _("项目key"), max_length=LEN_SHORT, null=False, default=0
    )

    @classmethod
    def create_record(cls, username, project_key):
        with transaction.atomic():
            cls.objects.create(
                creator=username, username=username, project_key=project_key
            )

    def update_record(self, project_key):
        with transaction.atomic():
            self.project_key = project_key
            self.updated_by = self.username
            self.save()


class ProjectConfig(Model):
    THEME_COLOR = [
        ("BLUE", "蓝色"),
        ("GREEN", "绿色"),
        ("ORANGE", "橙色"),
    ]
    theme = models.CharField(
        verbose_name=_("主题色"),
        null=False,
        default="BLUE",
        choices=THEME_COLOR,
        max_length=LEN_SHORT,
    )
    workflow_prefix = models.CharField(verbose_name="流程前缀", max_length=LEN_SHORT)
    project_key = models.CharField(
        verbose_name=_("产品"), max_length=LEN_SHORT, null=False, default=0
    )

    change_flag = True

    def tag_data(self):
        return {
            "theme": self.theme,
            "workflow_prefix": self.workflow_prefix,
            "project_key": self.project_key,
        }

    class Meta:
        verbose_name_plural = _("应用设置")
        verbose_name = _("应用设置")
