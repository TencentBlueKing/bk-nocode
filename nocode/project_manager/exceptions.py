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
from nocode.exceptions import ServerError

from django.utils.translation import ugettext as _


class ProjectConfigDoesNotExists(ServerError):
    MESSAGE = _("项目设置不存在")
    ERROR_CODE = "Project Does Not Exists"
    ERROR_CODE_INT = 4100001


class ProjectPublishError(ServerError):
    MESSAGE = _("项目版本发布失败")
    ERROR_CODE = "Project Publish Error"
    ERROR_CODE_INT = 4100002


class ProjectDoesNotExists(ServerError):
    MESSAGE = _("项目不存在")
    ERROR_CODE = "Project Does Not Exists"
    ERROR_CODE_INT = 4100003


class ProjectVersionDoesNotExists(ServerError):
    MESSAGE = _("项目版本不存在")
    ERROR_CODE = "Project Version Does Not Exists"
    ERROR_CODE_INT = 4100004


class PublishTaskDoesNotExists(ServerError):
    MESSAGE = _("发布任务不存在")
    ERROR_CODE = "Publish Task Does Not Exists"
    ERROR_CODE_INT = 4100005


class CreatePublishTaskError(ServerError):
    MESSAGE = _("发布失败，当前有正在发布的任务")
    ERROR_CODE = "Create Publish Task Error"
    ERROR_CODE_INT = 4100006


class MigrateUserGroupError(ServerError):
    MESSAGE = _("迁移用户组失败")
    ERROR_CODE = "Migrate User UserGroup Error"
    ERROR_CODE_INT = 4100007


class MigrateUserGroupPoliciesError(ServerError):
    MESSAGE = _("迁移用户组策略失败")
    ERROR_CODE = "Migrate User UserGroup Error Policies"
    ERROR_CODE_INT = 4100008


class MigrateUserGroupMemberError(ServerError):
    MESSAGE = _("用户组添加人员失败")
    ERROR_CODE = "Migrate User UserGroup Member Error"
    ERROR_CODE_INT = 4100009


class DeleteUserGroupMemberError(ServerError):
    MESSAGE = _("用户组删除失败")
    ERROR_CODE = "Delete User UserGroup Error"
    ERROR_CODE_INT = 4100010


class ProjectInitError(ServerError):
    MESSAGE = _("项目初始化失败")
    ERROR_CODE = "Project Init Error"
    ERROR_CODE_INT = 4100011


class WorkSheetInitError(ServerError):
    MESSAGE = _("工作表初始化失败")
    ERROR_CODE = "WorkSheet Init Error"
    ERROR_CODE_INT = 4100012


class WorkSheetFieldInitError(ServerError):
    MESSAGE = _("工作表字段初始化失败")
    ERROR_CODE = "WorkSheet Field Init Error"
    ERROR_CODE_INT = 4100013
