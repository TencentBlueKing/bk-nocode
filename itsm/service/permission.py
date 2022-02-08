# -*- coding: utf-8 -*-
from rest_framework import permissions
from django.utils.translation import ugettext as _

from itsm.project.handler.project_handler import ProjectHandler
from nocode.base.basic import check_user_owner_creator


class ServicePermission(permissions.BasePermission):

    message = _("您没有该应用操作的权限")

    def has_permission(self, request, view):
        need_permit_action = ["create"]
        if view.action in need_permit_action:
            project_key = request.data.get("project_key")
            project = ProjectHandler(project_key=project_key).instance
            user = request.user
            return check_user_owner_creator(user=user, project=project)
        return True

    def has_object_permission(self, request, view, obj, **kwargs):
        project = ProjectHandler(project_key=obj.project_key).instance
        user = request.user
        if view.action in ["update", "destroy", "save_configs"]:
            return check_user_owner_creator(user=user, project=project)
        return True
