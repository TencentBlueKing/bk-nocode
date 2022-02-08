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
from django.db import models

from nocode.base.base_model import Model
from django.utils.translation import ugettext as _

from nocode.base.constants import LEN_SHORT, LEN_NORMAL, LEN_LONG, LEN_X_LONG


class ProjectVersion(Model):
    """
    project_config
    page
    page_component
    worksheet
    filed
    """

    project_config = models.JSONField(_("项目配置"))
    page = models.JSONField(_("项目导航元信息"))
    page_component = models.JSONField(_("页面组件元信息"))
    worksheet = models.JSONField(_("项目工作表元信息"))
    worksheet_field = models.JSONField(_("项目工作表字段元信息"))
    version_number = models.CharField(
        _("版本号，32位uuid"), max_length=LEN_NORMAL, null=False
    )
    project_key = models.CharField(
        _("项目key"), max_length=LEN_SHORT, null=False, default=0
    )

    class Meta:
        app_label = "project_manager"


class OperateLog(Model):
    project_key = models.CharField(_("项目的key"), max_length=LEN_SHORT)
    module = models.CharField(_("模块"), max_length=LEN_LONG)
    content = models.CharField(_("操作内容"), max_length=LEN_LONG)
    operator = models.CharField(_("操作人"), max_length=LEN_SHORT)

    class Meta:
        app_label = "project_manager"


class PublishTask(Model):
    PUBLISH_STATUS = [
        ("CREATED", "未开始"),
        ("RUNNING", "正在发布"),
        ("FINISHED", "发布成功"),
        ("FAILED", "发布失败"),
    ]
    status = models.CharField(
        _("项目状态"),
        choices=PUBLISH_STATUS,
        default="CREATED",
        max_length=LEN_SHORT,
    )
    project_key = models.CharField(
        _("项目key"), max_length=LEN_SHORT, null=False, default=0
    )

    class Meta:
        app_label = "project_manager"


class PublishLog(models.Model):
    content = models.CharField(_("日志内容"), max_length=LEN_LONG)
    create_at = models.DateTimeField(_("创建时间"), auto_now_add=True)
    task_id = models.IntegerField(_("发布任务ID"))


class ProjectWhite(Model):
    TYPE_CHOICES = [
        ("WORKSHEET", "表单"),
        ("FUNCTION", "功能"),
    ]
    type = models.CharField(
        verbose_name=_("资源类型"), choices=TYPE_CHOICES, max_length=LEN_SHORT
    )
    value = models.IntegerField(verbose_name=_("资源id"), max_length=LEN_X_LONG)
    project_key = models.CharField(_("所属项目唯一标识"), max_length=LEN_SHORT)
    expired_at = models.DateTimeField(_("授权截止日期"), default="2099-12-12 00:00")
    granted_project = models.JSONField(_("被授权项目唯一标识"))

    class Meta:
        app_label = "project_manager"
