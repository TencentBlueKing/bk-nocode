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
from nocode.base.base_permission import PageDesignPermission
from nocode.base.basic import check_user_owner_creator
from nocode.page.models import Page


class PageComponentPermission(PageDesignPermission):
    def has_permission(self, request, view):
        if view.action == "batch_save":
            page = Page.objects.get(pk=request.data["page_id"])
            project = ProjectHandler(project_key=page.project_key).instance
            user = request.user
            return check_user_owner_creator(user=user, project=project)
        return True

    def has_object_permission(self, request, view, obj, **kwargs):
        page = Page.objects.get(pk=obj.page_id)
        obj = page
        return super(PageComponentPermission, self).has_object_permission(
            request, view, obj, **kwargs
        )


class OperateModelPermission(permissions.BasePermission):
    message = _("您暂无超级管理员权限，无法访问该页面")

    def has_permission(self, request, view):
        if view.action in ["list", "retrieve"]:
            if not request.user.is_superuser:
                return False
        return True

    def has_object_permission(self, request, view, obj, **kwargs):
        return True
