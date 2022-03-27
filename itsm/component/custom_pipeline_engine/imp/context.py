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

import json
from typing import Dict, List, Set

from django.db import transaction

from bamboo_engine import metrics
from bamboo_engine.eri import ContextValue, ContextValueType

from pipeline.eri.imp.serializer import SerializerMixin


class ContextMixin(SerializerMixin):
    @metrics.setup_histogram(metrics.ENGINE_RUNTIME_CONTEXT_VALUE_READ_TIME)
    def get_context_values(self, pipeline_id: str, keys: set) -> List[ContextValue]:
        """
        获取某个流程上下文中的 keys 所指定的键对应变量的值

        :param pipeline_id: 流程 ID
        :type pipeline_id: str
        :param keys: 变量键
        :type keys: set
        :return: 变量值信息
        :rtype: List[ContextValue]
        """

        data = []
        contexts_values = self.local.context_values.get(pipeline_id)
        for contexts_value in contexts_values:
            if contexts_value["key"] in keys:
                data.append(
                    ContextValue(
                        key=contexts_value["key"],
                        type=contexts_value["type"],
                        value=contexts_value["value"],
                        code=contexts_value.get("code") or None,
                    )
                )
        return data

    @metrics.setup_histogram(metrics.ENGINE_RUNTIME_CONTEXT_REF_READ_TIME)
    def get_context_key_references(self, pipeline_id: str, keys: set) -> set:
        """
        获取某个流程上下文中 keys 所指定的变量直接和间接引用的其他所有变量的键

        :param pipeline_id: 流程 ID
        :type pipeline_id: str
        :param keys: 变量 key 列表
        :type keys: set
        :return: keys 所指定的变量直接和简介引用的其他所有变量的键
        :rtype: set
        """
        references = []
        contexts_values = self.local.context_values.get(pipeline_id)
        for contexts_value in contexts_values:
            if contexts_value["key"] in keys:
                references.extend(json.loads(contexts_value["references"]))
        return set(references)

    @metrics.setup_histogram(metrics.ENGINE_RUNTIME_CONTEXT_VALUE_UPSERT_TIME)
    @transaction.atomic
    def upsert_plain_context_values(
        self, pipeline_id: str, update: Dict[str, ContextValue]
    ):
        """
        更新或创建新的普通上下文数据

        :param pipeline_id: 流程 ID
        :type pipeline_id: str
        :param update: 更新数据
        :type update: Dict[str, ContextValue]
        """
        contexts_values = self.local.context_values.get(pipeline_id)

        exist_keys = [contexts_value["key"] for contexts_value in contexts_values]
        update_keys = set(update.keys()).intersection(exist_keys)

        # update
        for k in update_keys:
            context_value = update[k]
            value, serializer = self._serialize(context_value.value)

            for cv in contexts_values:
                if cv["key"] == k:
                    cv["type"] = ContextValueType.PLAIN.value
                    cv["value"] = value
                    cv["serializer"] = (serializer,)
                    cv["code"] = ""
                    cv["references"] = "[]"

        # insert
        insert_keys = set(update.keys()).difference(exist_keys)
        for k in insert_keys:
            context_value = update[k]
            value, serializer = self._serialize(context_value.value)

            contexts_values.append(
                {
                    "key": context_value.key,
                    "type": ContextValueType.PLAIN.value,
                    "serializer": serializer,
                    "code": "",
                    "value": value,
                    "references": "[]",
                }
            )

    @metrics.setup_histogram(metrics.ENGINE_RUNTIME_CONTEXT_VALUE_READ_TIME)
    def get_context(self, pipeline_id: str) -> List[ContextValue]:
        """
        获取某个流程的所有上下文数据

        :param pipeline_id: 流程 ID
        :type pipeline_id: str
        :return: [description]
        :rtype: List[ContextValue]
        """
        contexts_values = self.local.context_values.get(pipeline_id)
        data = []
        for cv in contexts_values:
            data.append(
                ContextValue(
                    key=cv["key"],
                    type=ContextValueType(cv["type"]),
                    value=self._deserialize(cv["value"], cv["serializer"]),
                    code=cv.get("code") or None,
                )
            )

        return data

    def get_context_outputs(self, pipeline_id: str) -> Set[str]:
        """
        获取流程上下文需要输出的数据

        :param pipeline_id: 流程 ID
        :type pipeline_id: str
        :return: 输出数据 key
        :rtype: Set[str]
        """
        outputs = self.local.context_outputs.get(pipeline_id)["outputs"]
        return set(json.loads(outputs))
