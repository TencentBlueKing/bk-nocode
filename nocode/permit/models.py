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
from django.utils.translation import ugettext as _

from nocode.base.base_model import Model
from nocode.base.constants import LEN_SHORT, LEN_LONG


class UserGroup(Model):
    """
    用户组下的操作权限
    action_configs 协议:
    {
        page_view = [1, 2, 3, 4 ,6],
        action_execute = {
            page_id: [1, 2, 3, 5]
        }
    }
    """

    name = models.CharField(verbose_name=_("用户组名称"), max_length=LEN_SHORT)
    users = models.JSONField(_("用户列表"), default={})
    group_id = models.IntegerField(_("用户组ID"), default=0)
    action_configs = models.JSONField(_("权限配置"), default={})
    data_configs = models.JSONField(_("权限配置"), default={})
    desc = models.CharField(_("描述"), max_length=LEN_LONG, default="")
    project_key = models.CharField(
        _("项目key"), max_length=LEN_SHORT, null=False, default=0
    )

    class Meta:
        verbose_name_plural = _("用户组")
        verbose_name = _("用户组")
