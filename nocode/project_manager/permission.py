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
from rest_framework import permissions
from django.utils.translation import ugettext as _

from itsm.project.handler.project_handler import ProjectHandler
from nocode.base.base_permission import BasePermission
from nocode.base.basic import check_user_owner_creator
from nocode.project_manager.models import PublishTask


def publish_task(request):
    task_id = request.query_params.get("task_id")
    task = PublishTask.objects.get(id=task_id)
    return task.project_key


def get_method(request):
    return request.query_params.get("project_key")


def post_method(request):
    return request.data.get("project_key")


GET_PROJECT_KEY_MAP = {"publish_logs": publish_task, "publish": post_method}


class ProjectManagerPermission:
    def has_permission(self, request, view):
        return True


class ProjectAccessPermission:
    def has_permission(self, request, view):
        if view.action == "page_component":
            page_id = request.query_params.get("page_id")
            project_key = request.query_params.get("project_key")
            return BasePermission(request).have_page_access_resource(
                project_key, page_id
            )
        return True


class ProjectStatusPermission(permissions.BasePermission):
    message = _("您没有该应用操作的权限")

    def has_permission(self, request, view):
        project_key = request.query_params.get("project_key")
        if not project_key:
            self.message = _("缺少参数")
            return False
        project = ProjectHandler(project_key=project_key).instance
        if project.publish_status == "RELEASING":
            self.message = _("应用发布中，请稍后访问")
            return False
        return True


class SystemUserPermission(permissions.BasePermission):
    message = _("您暂无超级管理员权限，无法访问该页面")

    def superuser_permit(self, request):
        if not request.user.is_superuser:
            return False
        return True

    def has_permission(self, request, view):
        return self.superuser_permit(request)

    def has_object_permission(self, request, view, obj):
        return self.superuser_permit(request)


class WhiteListPermission(permissions.BasePermission):
    message = _("您没有该应用操作的权限")

    def has_object_permission(self, request, view, obj, **kwargs):
        project = ProjectHandler(project_key=obj.project_key).instance
        user = request.user
        if view.action in ["update", "destroy", "operate_white_list"]:
            return check_user_owner_creator(user=user, project=project)
        return True
