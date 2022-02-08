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
from nocode.project_manager.exceptions import (
    ProjectPublishError,
    CreatePublishTaskError,
)
from nocode.project_manager.handlers.module_handler import (
    ProjectModuleHandler,
    ServiceModuleHandler,
    UserGroupHandlerDispatcher,
)
from nocode.project_manager.handlers.project_version_handler import (
    ProjectVersionModelHandler,
    WorksheetIndexHandler,
    WorkSheetMigrateHandler,
)
from common.log import logger
from nocode.project_manager.handlers.publis_task_handler import PublishTaskHandler
from nocode.project_manager.handlers.publish_log_handler import PublishLogModelHandler
from nocode.project_manager.tasks import start_publish


class ProjectManagerHandler:
    def __init__(self, project_key):
        self.project_key = project_key

    def create_publish_task(self):
        handler = PublishTaskHandler(project_key=self.project_key)
        if handler.is_have_running_task():
            raise CreatePublishTaskError()
        task = handler.create_publish_task()
        start_publish.apply_async((task.id, self.project_key))
        return task


class PublishExecuteHandler:
    def __init__(self, project_key, task_id):
        self.project_key = project_key
        self.task_id = task_id
        self.handler = PublishLogModelHandler(task_id=self.task_id)

    def publish(self):

        self.handler.create_log("开始发布应用...")

        project_module_handler = ProjectModuleHandler(self.project_key)
        project_module_handler.update_status()

        task = PublishTaskHandler(task_id=self.task_id).get_instance()
        task.status = "RUNNING"
        task.save()

        try:
            # 变更应用状态为发布中
            project_module_handler.updating()
            self.handler.create_log("正在更新所有字段信息...")
            # 更新所有字段详情信息
            WorksheetIndexHandler(
                self.project_key, self.handler
            ).migrate_worksheet_fields()
            # 删除被删除的工作表:
            WorkSheetMigrateHandler(
                project_key=self.project_key, log_handler=self.handler
            ).migrate_worksheet()
            # 生成一个新的版本
            self.handler.create_log("正在准备创建新的应用版本...")
            version = ProjectVersionModelHandler(
                self.project_key, log_handler=self.handler
            ).create_version()
            # 更新版本号
            self.handler.create_log("正在准备更新应用绑定的版本信息...")
            project_module_handler.update_version(version.version_number)
            self.handler.create_log("版本信息更新完成...")
            self.handler.create_log("正在准备更新应用下的服务信息...")
            # 更新所有服务
            ServiceModuleHandler(project_key=self.project_key).update_service()
            self.handler.create_log("应用功能最新版本已同步..")

            self.handler.create_log("正在准备发布用户组...")

            # 迁移权限中心用户组
            UserGroupHandlerDispatcher(project_key=self.project_key).publish()

            task.status = "FINISHED"
            task.save()
            self.handler.create_log("应用发布成功...")

        except Exception as e:
            task.status = "FAILED"
            task.save()
            self.handler.create_log("应用发布失败, error={}...".format(e))
            logger.error("应用版本变更失败, error=={}".format(e))
            project_module_handler.update_failed()
            raise ProjectPublishError()
