# -*- coding: utf-8 -*-
from itsm.component.exceptions import ServerError
from django.utils.translation import ugettext as _


class InitGradeManagerError(ServerError):
    MESSAGE = _("初始化分级管理员失败")
    ERROR_CODE = "Init Grade Manager Error"
    ERROR_CODE_INT = 4200001


class InitUserGroupError(ServerError):
    MESSAGE = _("初始化用户组失败")
    ERROR_CODE = "Init User Group Error"
    ERROR_CODE_INT = 4200002


class InitUserGroupPolicesError(ServerError):
    MESSAGE = _("初始化用户组策略失败")
    ERROR_CODE = "Init User Group Polices Error"
    ERROR_CODE_INT = 4200003


class InitUserGroupMembersError(ServerError):
    MESSAGE = _("添加用户组人员失败，请去权限中心配置相应人员信息")
    ERROR_CODE = "Init User Group Members Error"
    ERROR_CODE_INT = 4200004


class DeleteCollectionError(ServerError):
    MESSAGE = _("用户收藏记录删除失败")
    ERROR_CODE = "Delete Collection Error"
    ERROR_CODE_INT = 4200005


class GetUserGroupError(ServerError):
    MESSAGE = _("获取用户组失败，请去权限中心查看")
    ERROR_CODE = "Get User Group Error"
    ERROR_CODE_INT = 4200006


class GetUserGroupMembersError(ServerError):
    MESSAGE = _("获取用户组人员失败，请去权限中心查看")
    ERROR_CODE = "Get User Group Members Error"
    ERROR_CODE_INT = 4200007


class DeleteUserGroupMembersError(ServerError):
    MESSAGE = _("移除用户组人员失败，请去权限中心配置相应人员信息")
    ERROR_CODE = "Delete User Group Members Error"
    ERROR_CODE_INT = 4200008
