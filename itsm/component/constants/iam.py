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

from settings import BK_IAM_SYSTEM_ID

BK_IAM_SYSTEM_ID = BK_IAM_SYSTEM_ID
ACTIONS = [
    {
        "id": "page_view",
        "name": "导航查看",
        "relate_resources": ["page"],
        "relate_actions": [],
        "resource_topo": ["project", "page"],
    },
    {
        "id": "project_admin",
        "name": "应用所有权限",
        "relate_resources": ["project"],
        "relate_actions": [],
        "resource_topo": ["project"],
    },
    {
        "id": "project_create",
        "name": "应用创建",
        "relate_resources": ["project"],
        "relate_actions": [],
        "resource_topo": [],
    },
    {
        "id": "action_execute",
        "name": "动作执行",
        "relate_resources": ["action"],
        "relate_actions": [],
        "resource_topo": ["project", "page", "action"],
    },
]

RESOURCES = [
    # 当前默认一个项目，所有的操作都在默认项目下操作
    {"id": "project", "name": "项目", "parent_id": None},
    # 服务，对应服务管理
    {"id": "page", "name": "页面", "parent_id": "project"},
    # 对应流程设计
    {"id": "action", "name": "操作", "parent_id": "page"},
]

BK_IAM_SYSTEM_NAME = "无代码平台"

HTTP_499_IAM_FORBIDDEN = 499

# 当前的应用，默认只有一个
PROJECT_INFO = {
    "resource_id": "0",
    "resource_name": "默认应用",
    "resource_type": "project",
    "resource_type_name": "应用",
}

PLATFORM_PERMISSION = ["project_create"]

IAM_SEARCH_INSTANCE_CACHE_TIME = 10 * 60  # 缓存5分钟
