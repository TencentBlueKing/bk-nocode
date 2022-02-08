# -*- coding: utf-8 -*-
from rest_framework import permissions
from django.utils.translation import ugettext as _

from nocode.base.base_permission import BasePermission
from nocode.base.basic import check_user_owner_creator


class ProjectPermission(permissions.BasePermission):

    message = _("您不是该应用管理员,无权访问该模块")

    def has_permission(self, request, view):
        if view.action == "create":
            self.message = _("您无权限进行应用创建，请先申请")
            return self.have_project_create_permit(request)
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        if view.action in ["update", "destroy"]:
            return check_user_owner_creator(user=user, project=obj)
        project_manager_action = ["operate_project_manager", "get_project_manager"]
        if view.action in project_manager_action and not request.user.is_superuser:
            self.message = _("您不是超级管理员,无权访问该模块")
            return False
        return True

    def have_project_create_permit(self, request):
        return BasePermission(request).have_project_create_permit()
