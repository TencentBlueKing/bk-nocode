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
import json
import os
from wsgiref.util import FileWrapper

from django.conf import settings
from django.http import StreamingHttpResponse
from rest_framework import serializers
from rest_framework.decorators import action
from django.utils.translation import ugettext as _
from django.utils.encoding import escape_uri_path

from common.log import logger
from itsm.component.drf.serializers import AuthModelSerializer
from itsm.component.drf.viewsets import AuthModelViewSet
from itsm.iadmin.models import SystemSettings
from itsm.project.models import Project
from nocode.base.base_viewset import BaseModelViewSet
from nocode.data_engine.core.db import DjangoBackend
from nocode.data_engine.core.managers import DataManager
from nocode.utils.worksheet_tool import (
    WorksheetAutoInit,
    ServiceMigrate,
    ServiceManager,
)

store = settings.STORE


class BaseModelViewSet(BaseModelViewSet):
    pass


class AuthModelSerializer(AuthModelSerializer):
    pass


class AuthModelViewSet(AuthModelViewSet):
    pass


class BaseFieldViewSet(BaseModelViewSet):
    @action(detail=True, methods=["get"])
    def download_file(self, request, *args, **kwargs):
        unique_key = request.GET.get("unique_key")
        file_type = request.GET.get("file_type")
        field_object = self.get_object()

        if field_object.type != "FILE":
            raise serializers.ValidationError(_("当前字段非附件字段，无法下载附件文件！"))
        try:
            files = (
                field_object.choice
                if file_type in ["template", "version"]
                else json.loads(field_object.value)
            )
        except Exception:
            logger.exception("json解析错误")
            raise serializers.ValidationError(_("当前字段解析信息出错，请确认是否已进行数据升级！"))

        file_info = files.get(unique_key)
        if not file_info:
            raise serializers.ValidationError(_("当前字段不存在您需要下载的附件！"))

        system_file_path = SystemSettings.objects.get(key="SYS_FILE_PATH").value
        file_path = os.path.join(system_file_path, file_info["path"])

        if not store.exists(file_path):
            raise serializers.ValidationError(
                _("要下载的文件【{}】不存在, 可能已经被删除，请与管理员确认！").format(file_info["name"])
            )

        response = StreamingHttpResponse(FileWrapper(store.open(file_path, "rb"), 512))
        response["Content-Type"] = "application/octet-stream"
        response["Content-Disposition"] = "attachment; filename* = UTF-8''{}".format(
            escape_uri_path(file_info["name"])
        )
        return response


class ProjectHandler:
    def __init__(self, project_key=None):
        self.project_key = project_key

    def exist(self):
        try:
            Project.objects.get(key=self.project_key)
        except Project.DoesNotExist:
            return False
        return True


class DjangoHandler:
    def __init__(self, db_name):
        self.db_name = db_name

    def init_db(self):
        DjangoBackend(self.db_name).create_table()


class DataMangerHandler:
    def __init__(self, worksheet_id):
        self.worksheet_id = worksheet_id

    @property
    def manager(self):
        return DataManager(worksheet_id=self.worksheet_id)

    def create_unique_index(self, key):
        self.manager.create_unique_index(key)

    def drop_unique_index(self, key):
        self.manager.drop_unique_index(key)


class ServiceHandler:
    def __init__(self, instance):
        self.instance = instance

    def init_service(self):
        WorksheetAutoInit(
            worksheet_id=self.instance.id,
            username="admin",
            project_key=self.instance.project_key,
        )()

    def migrate_service(self):
        ServiceMigrate(self.instance.id)()

    def migrate_service_name(self):
        ServiceMigrate(self.instance.id)

    def delete_service(self):
        ServiceManager(self.instance).delete_service()
