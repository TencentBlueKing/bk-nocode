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

from itsm.auth_iam.resources.basic import ItsmResourceProvider

from .basic import ItsmResourceListResult as ListResult
from ...component.constants import PUBLIC_PROJECT_PROJECT_KEY
from ...postman.models import RemoteSystem, RemoteApi


class PublicApiResourceProvider(ItsmResourceProvider):
    public_system_ids = RemoteSystem.objects.filter(project_key=PUBLIC_PROJECT_PROJECT_KEY).values_list("id", flat=True)
    queryset = RemoteApi.objects.filter(remote_system_id__in=public_system_ids, is_deleted=False)

    def list_instance(self, filter, page, **options):
        queryset = self.queryset
        count = queryset.count()
        # return 
        results = [{"id": remote_api.id, "display_name": remote_api.name} for remote_api in
                   queryset[page.slice_from: page.slice_to]]

        return ListResult(results=results, count=count)

    def fetch_instance_info(self, filter, **options):
        """
        flow 没有定义属性，只处理 filter 中的 ids 字段
        """
        queryset = self.queryset.filter(key__in=filter.ids)
        count = queryset.count()
        results = [{"id": remote_api.id, "display_name": remote_api.name} for remote_api in queryset]
        return ListResult(results=results, count=count)
