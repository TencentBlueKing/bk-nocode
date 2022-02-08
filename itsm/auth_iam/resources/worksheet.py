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

# from iam import PathEqDjangoQuerySetConverter
from common.log import logger
from itsm.auth_iam.resources import ItsmResourceProvider
from nocode.data_engine.core.managers import DataManager
from nocode.worksheet.models import WorkSheet
from .basic import ItsmResourceListResult as ListResult


class WorkSheetResourceProvider(ItsmResourceProvider):
    project_key = None
    worksheet_key = None

    def list_instance(self, filter, page, **options):
        """
        flow 上层资源为 project
        """

        logger.info("project_key is {}".format(self.project_key))
        logger.info("worksheet_key is {}".format(self.worksheet_key))

        worksheet = WorkSheet.objects.filter(
            project_key=self.project_key, key=self.worksheet_key
        ).first()
        queryset = DataManager(worksheet.id).get_queryset()
        count = queryset.count()
        # return
        results = [
            {"id": item.id, "display_name": "data[ID:{}]".format(item.id)}
            for item in queryset[page.slice_from : page.slice_to]
        ]
        return ListResult(results=results, count=count)
