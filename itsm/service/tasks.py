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

__author__ = "蓝鲸智云"
__copyright__ = "Copyright © 2012-2020 Tencent BlueKing. All Rights Reserved."

from celery.task import task

from common.log import logger
from itsm.ticket.tasks import start_pipeline

from itsm.service.models import PeriodicTask
from itsm.ticket.serializers import TicketSerializer


@task
def periodic_task_start(*args, **kwargs):
    service_id = kwargs["service_id"]
    logger.info("[periodic_task_start] 正在执行周期任务，service_id={}".format(service_id))
    # 应用发布之前，可能删除了某个周期任务，应用发布态的定时任务应当不受到
    periodic_task = (
        PeriodicTask._objects.filter(service_id=service_id)
        .order_by("-create_at")
        .first()
    )
    if periodic_task is None:
        logger.info(
            "[periodic_task_start] 定时任务执行取消, 配置不存在，service_id={}".format(service_id)
        )
        return

    periodic_task.total_run_count = periodic_task.total_run_count + 1
    periodic_task.save()

    fields = periodic_task.config.get("fields", [])
    data = {"service_id": periodic_task.service_id, "fields": fields, "creator": "auto"}
    try:
        logger.info("[periodic_task_start] 正在准备创建单据，data={}".format(data))
        serializer = TicketSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
    except Exception as e:
        logger.info(
            "[periodic_task_start] 周期触发单据创建异常，error={}, data={}".format(e, data)
        )
        return

    try:
        logger.info("[periodic_task_start] 单据创建完成，正在初始化单据字段，data={}".format(data))
        instance.do_after_create(data["fields"], None)
    except Exception as e:
        logger.info("[periodic_task_start] 初始化单据字段异常，error={}, data={}".format(e, data))
        instance.delete()
        logger.info(
            "[periodic_task_start] 异常单据已经删除，ticket_id={}, sn={}".format(
                instance.id, instance.sn
            )
        )
        return

    start_pipeline.apply_async([instance])
