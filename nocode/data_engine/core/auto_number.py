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
import datetime
import logging

import json
from django.conf import settings
from django_celery_beat.models import PeriodicTask, CrontabSchedule

logger = logging.getLogger("celery")


class BaseGenerator:
    generator_type = None

    def __init__(self, field, config, *args, **kwargs):
        self.field = field
        self.config = config

    def generate_number(self):
        pass


class DateGenerator(BaseGenerator):
    generator_type = "datetime"

    def __init__(self, field, config, *args, **kwargs):
        self.field = field
        self.config = config
        self.format_map = {
            "YYYY-MM-DD": "{}/{}/{}",
            "YYYY-MM": "{}/{}",
            "YYYY": "{}",
            "MM-DD": "{}/{}",
        }
        super(DateGenerator, self).__init__(field, config, *args, **kwargs)

    def generate_number(self):
        now = datetime.datetime.now()
        if self.config["value"] == "YYYY-MM-DD":
            return self.format_map["YYYY-MM-DD"].format(now.year, now.month, now.day)

        if self.config["value"] == "YYYY-MM":
            return self.format_map["YYYY-MM"].format(now.year, now.month)

        if self.config["value"] == "YYYY":
            return self.format_map["YYYY-MM-DD"].format(now.year)

        if self.config["value"] == "MM-DD":
            return self.format_map["MM-DD"].format(now.month, now.day)


class NumberGenerator(BaseGenerator):
    """
    {
        "length": ""
        "type": "number",
        "vlaue": 1, 起始位置
        "period_type": "0/day/week/month/year" 重置周期类型
        "format": "0/1" 0:重置成1， 1:重置为用户设定
    },
    """

    generator_type = "number"

    def __init__(self, field, config, *args, **kwargs):
        self.period_method = self.period_crontab_map()
        super(NumberGenerator, self).__init__(field, config, *args, **kwargs)

    def period_crontab_map(self):
        day_crontab, created = CrontabSchedule.objects.get_or_create(
            minute=0,
            hour=0,
            day_of_week="*",
            day_of_month="*",
            month_of_year="*",
            # minute='*/1', hour="*", day_of_week="*", day_of_month="*", month_of_year="*",
            timezone="Asia/Shanghai",
        )
        week_crontab, created = CrontabSchedule.objects.get_or_create(
            minute=0,
            hour=0,
            day_of_week=1,
            day_of_month="*",
            month_of_year="*",
            timezone="Asia/Shanghai",
        )
        month_crontab, created = CrontabSchedule.objects.get_or_create(
            minute=0,
            hour=0,
            day_of_week="*",
            day_of_month=1,
            month_of_year="*",
            timezone="Asia/Shanghai",
        )
        year_crontab, _ = CrontabSchedule.objects.get_or_create(
            minute=0,
            hour=0,
            day_of_week="*",
            day_of_month=1,
            month_of_year=1,
            timezone="Asia/Shanghai",
        )
        return {
            "day": day_crontab,
            "week": week_crontab,
            "month": month_crontab,
            "year": year_crontab,
        }

    def get_creat_period_reset(self, key):
        crontab_type = self.period_method.get(self.config["period_type"], None)
        if not crontab_type:
            return
        try:

            PeriodicTask.objects.get(
                name=key,
                crontab=crontab_type,
                task="nocode.data_engine.core.utils.value_reset",
                args=json.dumps(
                    [key, self.config.get("value"), int(self.config.get("format", 0))]
                ),
                enabled=True,
            )
        except PeriodicTask.DoesNotExist:
            # 更新定时任务
            history_task = PeriodicTask.objects.filter(
                name=key, task="nocode.data_engine.core.utils.value_reset", enabled=True
            )
            if history_task:
                item = {
                    "crontab": crontab_type,
                    "args": json.dumps(
                        [
                            key,
                            self.config.get("value"),
                            int(self.config.get("format", 0)),
                        ]
                    ),
                }
                try:
                    history_task.update(**item)
                except Exception as e:
                    logger.error(f"update PeriodicTask failed: {e}")
            else:
                # 没有则创建
                try:
                    PeriodicTask.objects.create(
                        name=key,
                        crontab=crontab_type,
                        task="nocode.data_engine.core.utils.value_reset",
                        args=json.dumps(
                            [
                                key,
                                self.config.get("value"),
                                int(self.config.get("format", 0)),
                            ]
                        ),
                    )
                except Exception as e:
                    logger.error(f"create PeriodicTask failed: {e}")

    def generate_number(self):
        key = "{}_{}_{}".format(
            self.field["worksheet_id"], self.field["id"], self.field["key"]
        )

        # 是否存在这个值
        value_in_redis = settings.REDIS_INST.get(key)

        # 动态添加周期重置定时任务
        self.get_creat_period_reset(key)

        # 当获取value存在或者被重置为设置的初始值
        if not value_in_redis:
            value = str(settings.REDIS_INST.incrby(key, int(self.config.get("value"))))
        # 继续累加
        else:
            value = settings.REDIS_INST.incrby(key)
        return str(value).rjust(int(self.config["length"]), "0")


class ConstGenerator(BaseGenerator):
    generator_type = "const"

    """
    {
        "type": "const/field",
        "value": "define/field_key",
    }
    """

    def __init__(self, field, config, *args, **kwargs):
        self.validated_data = kwargs.get("validated_data", {})
        super(ConstGenerator, self).__init__(field, config, *args, **kwargs)

    def generate_number(self):
        if self.config["type"] == "const":
            return self.config.get("value", "")
        if self.config["type"] == "field":
            return self.validated_data.get(self.config["value"], "")


class NumberGeneratorDispatcher:
    GENERATE_MAP = {
        "const": ConstGenerator,
        "datetime": DateGenerator,
        "number": NumberGenerator,
        "field": ConstGenerator,
    }

    def __init__(self, filed, validated_data):
        if isinstance(filed["meta"], str):
            meta = json.loads(filed["meta"])
        else:
            meta = filed["meta"]
        self.configs = meta.get("config", [])
        self.filed = filed
        self.validated_data = validated_data

    def generate_number(self):
        """
        {
            "config": [
                {

                    "type": "number",
                    "vlaue": 1, 起始位置
                    "period_type": "0/day/month/year" 重置周期类型
                    "length": 位数
                    "format": ""

                },
                {
                    "type": "datetime"
                    "value": YYYYMMDD
                },
                {
                    "type": "const",
                    "value": "",
                },
                {
                    "type": "field",
                    "value": "field_key"
                }
            ]
        }
        """

        number = []
        for config in self.configs:
            n = self.GENERATE_MAP[config["type"]](
                self.filed, config, validated_data=self.validated_data
            ).generate_number()
            number.append(n)

        return "-".join(number)
