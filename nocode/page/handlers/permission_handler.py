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
from django.utils.translation import ugettext as _

from itsm.project.handler.project_handler import ProjectHandler
from nocode.base.base_permission import PageDesignPermission
from nocode.base.basic import check_user_owner_creator
from nocode.base.constants import OPEN
from nocode.page.handlers.role_handler import RoleHandler


class PageViewPermission(PageDesignPermission):
    """
    页面查看权限鉴权
    """

    message = _("您没有该应用操作的权限")

    def has_permission(self, request, view):

        if view.action in ["create", "update", "destroy"]:
            project_key = request.query_params.get("project_key") or request.data.get(
                "project_key"
            )
            if not project_key:
                self.message = _("缺少project_key参数")
                return False
            project = ProjectHandler(project_key=project_key).instance
            return check_user_owner_creator(user=request.user, project=project)
        return True

    def has_object_permission(self, request, view, obj, **kwargs):
        # 关联实例的请求，需要针对对象进行角色鉴权
        if view.action in ["children", "retrieve"]:
            if obj.display_type == OPEN:
                return True
            # 获取当前用户的角色
            user = request.user
            # 获取展示范围成语
            members = RoleHandler.get_users_by_role(
                display_type=obj.display_type,
                display_role=obj.display_role,
                project_key=obj.project_key,
            )
            if user.username not in members:
                return False

        project = ProjectHandler(project_key=obj.project_key).instance
        if view.action in [
            "move",
            "parent_migrate",
            "change_display",
            "update",
            "destroy",
        ]:
            user = request.user
            return check_user_owner_creator(project=project, user=user)
        return True
