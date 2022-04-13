# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from typing import List
from datetime import datetime

from bamboo_engine.eri import ExecutionHistory, ExecutionShortHistory
from pipeline.eri.imp.serializer import SerializerMixin


class ExecutionHistoryMixin(SerializerMixin):
    def add_history(
        self,
        node_id: str,
        started_time: datetime,
        archived_time: datetime,
        loop: int,
        skip: bool,
        retry: int,
        version: str,
        inputs: dict,
        outputs: dict,
    ) -> int:
        """
        为某个节点记录一次执行历史

        : param node_id: 节点 ID
        : type node_id: str
        : param started_time: 开始时间
        : type started_time: datetime
        : param archived_time: 归档时间
        : type archived_time: datetime
        : param loop: 重入计数
        : type loop: int
        : param skip: 是否跳过
        : type skip: bool
        : param retry: 重试次数
        : type retry: int
        : param version: 节点执行版本号
        : type version: str
        : param inputs: 输入数据
        : type inputs: dict
        : param outputs: 输出数据
        : type outputs: dict
        """
        pass

    def get_histories(self, node_id: str, loop: int = -1) -> List[ExecutionHistory]:
        """
        返回某个节点的历史记录

        :param node_id: 节点 ID
        :type node_id: str
        :param loop: 重入次数, -1 表示不过滤重入次数
        :type loop: int, optional
        :return: 历史记录列表
        :rtype: List[History]
        """
        pass

    def get_short_histories(
        self, node_id: str, loop: int = -1
    ) -> List[ExecutionShortHistory]:
        """
        返回某个节点的简要历史记录

        :param node_id: 节点 ID
        :type node_id: str
        :param loop: 重入次数, -1 表示不过滤重入次数
        :type loop: int, optional
        :return: 历史记录列表
        :rtype: List[ExecutionShortHistory]
        """
        pass
