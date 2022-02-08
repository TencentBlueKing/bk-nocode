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

from django.conf import settings
from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from blueapps.account.decorators import login_exempt
from iam import IAM
from iam.contrib.django.dispatcher import DjangoBasicResourceApiDispatcher
from itsm.auth_iam.resources import ProjectResourceProvider
from itsm.auth_iam.resources.action import ActionResourceProvider
from itsm.auth_iam.resources.page import PageResourceProvider
from itsm.auth_iam.views import ResourceViewSet, PermissionViewSet

iam = IAM(
    settings.APP_CODE,
    settings.SECRET_KEY,
    settings.BK_IAM_INNER_HOST,
    settings.BK_PAAS_HOST,
)

routers = DefaultRouter(trailing_slash=True)

routers.register(r"__skip__", ResourceViewSet, basename="skip")
routers.register(r"permission", PermissionViewSet, basename="permissions")

# 注册权限资源接口
dispatcher = DjangoBasicResourceApiDispatcher(iam, settings.BK_IAM_SYSTEM_ID)
dispatcher.register("project", ProjectResourceProvider())
dispatcher.register("page", PageResourceProvider())
dispatcher.register("action", ActionResourceProvider())

urlpatterns = routers.urls + [
    url(r"^resources/v1/$", dispatcher.as_view([login_exempt])),
]
