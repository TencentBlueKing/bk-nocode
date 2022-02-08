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
from celery.task import task

from common.log import logger
from itsm.project.handler.worksheet_handler import WorkSheetModelHandler


@task
def migrate_service(worksheet_id):
    logger.info("开始迁移功能字段, worksheet_id = {}".format(worksheet_id))

    try:
        instance = WorkSheetModelHandler(worksheet_id=worksheet_id).instance
    except Exception:
        logger.info("迁移失败, worksheet_id = {} 的工作表不存在".format(worksheet_id))
        return

    from nocode.worksheet.handlers.moudule_handler import ServiceHandler

    try:
        ServiceHandler(instance).migrate_service()
    except Exception as e:
        import traceback

        traceback.print_exc()
        logger.info("迁移失败, worksheet_id = {}, error={}".format(worksheet_id, e))
        return

    logger.info("功能字段迁移成功, worksheet_id = {}".format(worksheet_id))
