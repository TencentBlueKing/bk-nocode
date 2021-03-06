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
import ast
import codecs
import csv
import datetime
import json
import re

import openpyxl
from django.db.models import Count
from django.http import HttpResponse
from rest_framework.response import Response

from common.log import logger
from itsm.component.drf.pagination import CustomPageNumberPagination
from nocode.data_engine.core.constants import DAY, MONTH, YEAR
from nocode.data_engine.core.managers import DataManager

from nocode.data_engine.core.utils import ConditionTransfer
from nocode.data_engine.exceptions import (
    GetDetailDataError,
    ImportDataError,
    DataValidateError,
)
from nocode.data_engine.handlers.module_handlers import (
    PageComponentHandler,
    ServiceHandler,
)
from nocode.project_manager.models import ProjectVersion


class BaseDataHandler:
    def get_response_data(self, page_queryset):
        """
        查询到的值去掉contents__前缀
        """
        data = []
        for item in page_queryset:
            new_item = {}
            for key, value in item.items():
                new_item[key.replace("contents__", "", 1)] = value
            data.append(new_item)

        return data

    def convert_conditions(self, conditions):
        transfer = ConditionTransfer(conditions)
        return transfer.trans()

    def get_config(self, config):
        # 对之前对数据做兼容
        if isinstance(config, str):
            return json.loads(config)
        return config


class ListComponentDataHandler(BaseDataHandler):
    def __init__(self, page_id, request, version_number):
        self.request = request
        self.page_id = page_id
        self.version_number = version_number

    def get_list_components_data(self, conditions=None, need_page=True):
        """
        获取列表组件的data
        """
        if conditions is None:
            conditions = {}

        filters = self.convert_conditions(conditions)

        page_config = PageComponentHandler.get_list_component_config(
            self.page_id, self.version_number
        )
        worksheet_id = page_config["value"]

        logger.info(
            "[get_list_components_data] -> worksheet_id={}".format(worksheet_id)
        )

        manager = DataManager(worksheet_id)
        fields = manager.fields
        keys, upload_fields = self.get_keys(page_config["config"], fields)
        logger.info("[get_list_components_data] -> keys={}".format(keys))

        page_config_queryset = self.get_page_config_queryset(
            manager, page_config["config"]
        )
        if not page_config_queryset:
            queryset = []
        else:
            queryset = page_config_queryset.filter(filters).values(*keys)

        if upload_fields:
            for item in queryset:
                for field in upload_fields:
                    if item[field]:
                        # 列表字符串转换成列表
                        try:
                            item[field] = ast.literal_eval(item[field])
                        except SyntaxError:
                            logger.warn(f"{field} -> 参数传输有误 {item[field]}")
                            continue
                    else:
                        item[field] = []
        logger.info("[get_list_components_data] -> queryset={}".format(queryset))
        if not need_page:
            return Response(self.get_response_data(queryset))
        pagination = CustomPageNumberPagination()
        page_queryset = pagination.paginate_queryset(queryset, self.request)
        return pagination.get_paginated_response(self.get_response_data(page_queryset))

    def get_page_config_queryset(self, manager, config):
        """
        "show_mode": {
            "mode": 0,1,2
            "show_condition":[
                {
                    # 设置指定用户
                    "set_user_range": {
                        "members_group":[],
                        "members":[],
                        "condition": 0,1,2
                    },
                    # 展示相应用用户的数据
                    "display_user_range": {
                        "members_group":[],
                        "members":[]
                    },
                },
                ...
            ]
        }
        """
        config = self.get_config(config)
        queryset = manager.get_queryset()

        ordering = config.get("ordering", [])

        # 排序字段支持
        if len(ordering) > 1:
            queryset = queryset.order_by(ordering[0])
        # 筛选条件支持
        conditions = config.get("conditions", {})
        filters = self.convert_conditions(conditions)

        if conditions:
            queryset = queryset.filter(filters)

        # 0:展示所有数据，1:展示用户自己的数据, 2:展示范围选择
        show_mode = config.get("show_mode", {})
        if not show_mode or show_mode["mode"] == 0:
            return queryset

        if show_mode["mode"] == 1:
            queryset = queryset.filter(creator=self.request.user.username)

        # 选择范围显示
        if show_mode["mode"] == 2:
            # username = self.request.user.username
            display_role = show_mode["display_role"].split(",")
            queryset = queryset.filter(creator__in=display_role)

        return queryset

    def export_list_component_data(self, conditions=None, ids=None):

        if not conditions:
            conditions = {}

        filters = self.convert_conditions(conditions)

        page_config = PageComponentHandler.get_list_component_config(
            self.page_id, self.version_number
        )
        worksheet_id = page_config["value"]
        manager = DataManager(worksheet_id)
        fields = manager.fields
        # 获取所要展示自定义字段
        keys, _ = self.get_keys(page_config["config"], fields)
        # 导出批量记录
        if ids:
            base_queryset = manager.get_queryset().filter(id__in=ids)
        else:
            base_queryset = manager.get_queryset()
        queryset = base_queryset.filter(filters).values(*keys)

        key_map = self.get_key_map(fields)

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment;filename={}.csv".format(
            manager.worksheet.name
        )

        response.write(codecs.BOM_UTF8)

        head_fields = self.get_filter_fields(page_config["config"], fields)

        writer = csv.writer(response)
        head = [f["name"] for f in head_fields]
        head.insert(0, "序号")
        writer.writerow(head)
        for row, values in enumerate(queryset):
            fields = [row + 1]
            for index, key in enumerate(keys):
                if key in key_map:
                    choices = key_map.get(key).get("choice", [])
                    try:
                        choice_keys = values.get(key, "--").split(",")
                    except Exception:
                        fields.append("")
                        continue

                    choice_map = {item["key"]: item["name"] for item in choices}
                    value = ""
                    for choice_key in choice_keys:
                        value += choice_map.get(choice_key, "") + ","
                    value = value.strip(",")
                    fields.append(value)
                else:
                    fields.append(values.get(key, "--"))
            writer.writerow(fields)

        return response

    def get_filter_fields(self, config, fields):
        filter_fields = [{"name": "id"}]
        config = self.get_config(config)
        field_ids = config.get("fields", [])
        sys_fields = config.get("sys_fields", [])
        for field in fields:
            if field["id"] in field_ids:
                filter_fields.append(field)

        sys_dict = {
            "creator": "提交人",
            "update_at": "更新时间",
            "create_at": "创建时间",
            "updated_by": "更新人",
        }
        for sys_field in sys_fields:
            filter_fields.append({"name": sys_dict.get(sys_field)})
        return filter_fields

    def get_key_map(self, fields):
        key_map = {}  # {contents__id: choices}
        for field in fields:
            key = "contents__{}".format(field["key"])
            if field["type"] in [
                "SELECT",
                "INPUTSELECT",
                "MULTISELECT",
                "CHECKBOX",
                "RADIO",
            ]:
                key_map[key] = field

        return key_map

    def get_keys(self, config, fields):
        """
        计算出列表所需要展示的字段的key列表
        """
        keys = ["id"]

        config = self.get_config(config)
        field_ids = config.get("fields", [])
        upload_fields = []
        for field in fields:
            if field["id"] in field_ids:
                keys.append("contents__{}".format(field["key"]))
                # 图片控件类型
                #
                if field["type"] in ["IMAGE", "FILE"]:
                    upload_fields.append("contents__{}".format(field["key"]))

        # 增加返回系统字段
        sys_fields = config.get("sys_fields", [])
        if sys_fields:
            keys += sys_fields
        return keys, upload_fields

    def generate_export_template(self):

        page_config = PageComponentHandler.get_list_component_config(
            self.page_id, self.version_number
        )
        worksheet_id = page_config["value"]
        manager = DataManager(worksheet_id)
        fields = manager.fields

        sheet_name = (
            manager.worksheet.name
            + "_"
            + datetime.datetime.now().strftime("%Y%m%d%H%M")
        )
        work_book = openpyxl.Workbook()
        ws = work_book.worksheets[0]
        print(["{}({})".format(value["name"], value["key"]) for value in fields])
        ws.append(["{}({})".format(value["name"], value["key"]) for value in fields])

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        # response = HttpResponse(content_type='application/vnd.ms-excel')
        response["Content-Disposition"] = "attachment; filename={}.xlsx".format(
            sheet_name
        )
        work_book.save(response)
        return response


class ListComponentDetailHandler(BaseDataHandler):
    def __init__(self, service_id, pk, worksheet_id):
        self.service_id = service_id
        self.pk = pk
        self.worksheet_id = worksheet_id

    def data(self):
        try:
            keys = ServiceHandler(
                service_id=self.service_id, worksheet_id=self.worksheet_id
            ).get_keys()
            manager = DataManager(self.worksheet_id)

            queryset = manager.get_queryset()

            queryset = queryset.filter(id=self.pk).values(*keys)
        except Exception as e:
            logger.info(
                "数据详情获取失败，service_id={}, worksheet_id={}, pk={},"
                "error={}".format(self.service_id, self.worksheet_id, self.pk, e)
            )
            raise GetDetailDataError()
        return self.get_response_data(queryset)


class WorkSheetDataHandler(BaseDataHandler):
    def __init__(self, worksheet_id, request):
        self.worksheet_id = worksheet_id
        self.request = request

    def data(self, conditions, fields, need_page):
        manager = DataManager(self.worksheet_id)
        keys = self.get_keys(fields)
        if not conditions["connector"] and not conditions["expressions"]:
            conditions = {}
        filters = self.convert_conditions(conditions)
        queryset = manager.get_queryset().filter(filters).values(*keys)
        if need_page:
            pagination = CustomPageNumberPagination()
            page_queryset = pagination.paginate_queryset(queryset, self.request)
            return pagination.get_paginated_response(
                self.get_response_data(page_queryset)
            )
        return self.get_response_data(queryset)

    def get_keys(self, fields):

        keys = ["id"]

        for field in fields:
            keys.append("contents__{}".format(field))
        return keys

    def get_fields_by_version(self, version_number):
        project_version = ProjectVersion.objects.get(version_number=version_number)
        worksheet_fields_version = project_version.worksheet_field[
            str(self.worksheet_id)
        ]

        data_struct = {}
        data_struct.setdefault(
            "fields", ["id", "create_at", "update_at", "creator", "updated_by"]
        )
        data_struct.setdefault("upload_fields", [])
        for field in worksheet_fields_version:
            data_struct["fields"].append("contents__{}".format(field["key"]))
            if field["type"] in ["IMAGE", "FILE"]:
                data_struct["upload_fields"].append("contents__{}".format(field["key"]))
        return data_struct

    def get_worksheet_data_by_version(self, version_number):
        keys = self.get_fields_by_version(version_number)
        manager = DataManager(self.worksheet_id)
        queryset = manager.get_queryset().values(*keys["fields"])

        if keys["upload_fields"]:
            for item in queryset:
                for field in keys["upload_fields"]:
                    if item[field]:
                        # 列表字符串转换成列表
                        try:
                            item[field] = ast.literal_eval(item[field])
                        except SyntaxError:
                            continue
                    else:
                        item[field] = []

        return self.get_response_data(queryset)


class ExportDataHandler:
    def __init__(self, worksheet_id, request):
        self.worksheet_id = worksheet_id
        self.pattern = re.compile(r"[(](.*?)[)]", re.S)
        self.request = request
        self.manager = DataManager(worksheet_id=self.worksheet_id)

    def get_keys(self, headers):
        keys = []
        for item in headers:
            key = self.pattern.findall(item)
            if len(key) != 1:
                raise ImportDataError(
                    "[ExportDataHandler][get_keys]数据导入失败，表头{}不符合规范".format(item)
                )
            keys.append(key[0])
        return keys

    def validate(self, file):
        try:
            results = {}
            wb = openpyxl.load_workbook(file)
            sheet = wb.worksheets[0]
            rows_count = sheet.max_row  # 行数
            logger.info(
                "[ExportDataHandler][import_by_excels] 正在导入数据，{}条".format(rows_count)
            )
            if rows_count > 1000:
                raise ImportDataError()
            headers = next(sheet.values)
            keys = self.get_keys(headers=headers)

            for index, rowValues in enumerate(sheet.values):
                if index == 0:
                    continue
                data = {}
                for key, value in zip(keys, rowValues):
                    if isinstance(value, datetime.datetime):
                        value = value.strftime("%Y-%m-%d %H:%M:%S")
                    data[key] = value
                try:
                    self.manager.serializer_validate(data)
                except Exception as e:
                    results[index] = str(e)
                    logger.info("数据校验失败，第{}行,错误原因 error={}".format(index, e))
            return results
        except Exception as e:
            raise DataValidateError("数据校验失败, 错误原因 error={}".format(e))

    def import_by_excels(self, file):
        wb = openpyxl.load_workbook(file)
        sheet = wb.worksheets[0]
        logger.info("[ExportDataHandler][import_by_excels] 正在校验数据的合法性")
        # 提前将所有数据的合法性校验一编
        rows_count = sheet.max_row  # 行数
        logger.info(
            "[ExportDataHandler][import_by_excels] 正在导入数据，{}条".format(rows_count)
        )
        headers = next(sheet.values)
        keys = self.get_keys(headers=headers)
        for index, rowValues in enumerate(sheet.values):
            if index == 0:
                continue
            data = {}
            for key, value in zip(keys, rowValues):
                if isinstance(value, datetime.datetime):
                    value = value.strftime("%Y-%m-%d %H:%M:%S")
                data[key] = value
            try:
                self.manager.add(data, self.request.user.username)
            except Exception as e:
                logger.info(
                    "[ExportDataHandler][import_by_excels] 数据导入失败，{}条, error={}".format(
                        rows_count, e
                    )
                )
                raise ImportDataError(
                    "[ExportDataHandler][import_by_excels] 数据导入失败，成功导入{}条".format(index)
                )
        return rows_count


class ChartDataHandler(ListComponentDataHandler):
    """
    {
        ...
        config：{
            name：图标名称,
            value：图表的类型,
        xaxes：{
            "key": field_key/create_at/update_at
            "type": const/time
            "value": (day/month/year)
            [value只针对create_at/update_at]
        },
        y_fields_list:  [
            {"type":}
        ],

        conditions:{
             expressions:[
                    {
                      "key": "create_at",
                      "type": "const",
                      "condition": "in",
                      "value": "1",
                    },
                    ...
                ]
        },

        }
    }

    """

    def __init__(self, page_component_id, page_id, request, version_number):
        self.page_component_id = page_component_id
        super(ChartDataHandler, self).__init__(
            page_id=page_id, request=request, version_number=version_number
        )

    def analysis(self):
        chart_configs = self.get_chart_config()
        if not chart_configs:
            return
        result = self.analysis_data(chart_configs)
        return result

    def get_chart_config(self):
        # 获取该页面下的所有图表组件的设置
        chart_configs = PageComponentHandler.get_chart_component_config(
            page_id=self.page_id,
            version_number=self.version_number,
            page_component_id=self.page_component_id,
        )
        if isinstance(chart_configs, str):
            chart_configs = json.loads(chart_configs)
        return chart_configs

    def analysis_data(self, chart_configs):
        all_chart = []
        for chart_config in chart_configs:
            # 获取chart组件设置
            worksheet_id = chart_config["value"]
            chart_setting = chart_config["config"]
            conditions = chart_setting["conditions"]

            # 数据调取
            manager = DataManager(worksheet_id)
            # 时间范围过滤条件
            time_filters = self.convert_conditions(conditions)
            # 时间范围过滤后所有数据
            queryset = manager.get_queryset().filter(time_filters)

            # 获取X轴过滤依据
            """
            {
                "key":field_key,
                "type": const/time,
                "value": (只针对type=time)
            ]
            """
            x_label_key = chart_setting["xaxes"]

            # 获取Y轴依据
            y_label_list = chart_setting["yaxis_list"]

            # all contents
            if x_label_key["type"] == "const":
                result = self.analysis_by_const(
                    queryset=queryset,
                    x_label_key=x_label_key,
                    y_label_list=y_label_list,
                    chart_setting=chart_setting,
                )
                all_chart.append(result)

            if x_label_key["type"] == "time":
                result = self.analysis_by_time(
                    queryset=queryset,
                    x_label_key=x_label_key,
                    y_label_list=y_label_list,
                    chart_setting=chart_setting,
                )
                all_chart.append(result)

        return all_chart

    def count(self, content_list):
        return len(content_list)

    def sum(self, content_list, depend_field):
        value = 0
        for content in content_list:
            value += content[depend_field]
        return value

    def analysis_by_time(self, queryset, x_label_key, y_label_list, chart_setting):
        """
        {
            "key":field_key,
            "type": const/time,
            "value": (只针对type=time)
        }
        """
        if x_label_key["key"] == "create_at":
            queryset.order_by("-create_at")
        if x_label_key["key"] == "update_at":
            queryset.order_by("-update_at")

        # 获取时间范围
        year_filter_1 = int(
            chart_setting["conditions"]["expressions"][0]["value"].split("-")[0]
        )
        year_filter_2 = int(
            chart_setting["conditions"]["expressions"][1]["value"].split("-")[0]
        )
        # 过滤年生成器
        first_params = min(year_filter_2, year_filter_1)
        second_prams = max(year_filter_2, year_filter_1)
        year_range = (
            range(first_params, second_prams + 1)
            if first_params != second_prams
            else [first_params]
        )

        sorted_content = self.sort_queryset_by_time(
            queryset=queryset,
            x_label_key=x_label_key,
            year_range=year_range,
            chart_setting=chart_setting,
        )

        y_result = self.analysis_after_sort_content(
            sorted_content=sorted_content, y_label_list=y_label_list
        )
        result = {"x_label": sorted_content.keys(), "y_list": y_result}
        result.update(
            {
                "name": chart_setting["name"],
                "value": chart_setting["value"],
            }
        )
        return result

    def analysis_by_const(self, queryset, x_label_key, y_label_list, chart_setting):
        # x轴分类的数据
        sorted_content = self.sort_queryset_by_key(queryset, x_label_key)
        # 根据y轴依据进行数据的统计
        y_result = self.analysis_after_sort_content(sorted_content, y_label_list)
        result = {"x_label": sorted_content.keys(), "y_list": y_result}
        result.update(
            {
                "name": chart_setting["name"],
                "value": chart_setting["value"],
            }
        )
        return result

    def analysis_after_sort_content(self, sorted_content, y_label_list):
        y_result = {}
        for field, content_list in sorted_content.items():
            y_result[field] = {}
            for y_label in y_label_list:
                # 创建分类的总数统计
                if y_label["type"] == "count":
                    y_result[field][y_label["type"]] = self.count(content_list)
                # 依据字段总计统计
                if y_label["type"] == "sum":
                    y_result[field][y_label["type"]] = self.sum(
                        content_list, y_label["field"]
                    )
        return y_result

    def sort_queryset_by_key(self, queryset, x_label_key):
        x_sort = []
        sorted_content = {}

        for item in queryset:
            content = (
                json.loads(item.contents)
                if isinstance(item.contents, str)
                else item.contents
            )
            # x轴 分类 同时根据x轴分类数据
            # 根据key，获取分类
            sort_value = content.get(x_label_key["key"])
            # 数据分类
            if sort_value in x_sort:
                sorted_content[sort_value].append(content)
            else:
                x_sort.append(sort_value)
                sorted_content.setdefault(sort_value, [content])
        return sorted_content

    def sort_queryset_by_time(self, queryset, x_label_key, year_range, chart_setting):
        """
        {
            "key":field_key,
            "type": const/time,
            "value": (只针对type=time)
        }
        """
        filter_condition = x_label_key["value"]
        # 按照天的分类
        if filter_condition == DAY:
            return self.sort_queryset_by_day(
                queryset=queryset,
                x_label_key=x_label_key,
                year_range=year_range,
                chart_setting=chart_setting,
            )

        # 按照每年月份的分类
        if filter_condition == MONTH:
            # 根据年月对content 进行分类
            return self.sort_queryset_by_month(
                queryset=queryset,
                x_label_key=x_label_key,
                year_range=year_range,
            )

        # 按照年分类
        if filter_condition == YEAR:
            return self.sort_queryset_by_year(
                queryset=queryset, x_label_key=x_label_key, year_range=year_range
            )

    def sort_queryset_by_day(self, queryset, x_label_key, year_range, chart_setting):
        x_sort = []
        sorted_content = {}
        for year in year_range:
            # 月
            month = chart_setting["conditions"]["expressions"]["0"]["value"].split("-")[
                1
            ]
            each_day_queryset = None
            if x_label_key["key"] == "create_at":
                filter_queryset = queryset.filter(
                    create_at__year=year, create_at__month=month
                )
                each_day_queryset = (
                    filter_queryset.extra(
                        select={"create_at": "DATE_FORMAT(create_at, '%%e')"}
                    )
                    .values("create_at")
                    .annotate(total=Count("create_at"))
                    .values("create_at", "total", "contents")
                )

            if x_label_key["key"] == "update_at":
                filter_queryset = queryset.filter(
                    update_at__year=year, update_at__month=month
                )
                each_day_queryset = (
                    filter_queryset.extra(
                        select={"update_at": "DATE_FORMAT(create_at, '%%e')"}
                    )
                    .values("update_at")
                    .annotate(total=Count("update_at"))
                    .values("update_at", "total", "contents")
                    .order_by("-create_at")
                )

            for item in each_day_queryset:
                create_at_day = item.get("create_at")
                sort_value = f"{year}-{month}-{create_at_day}"

                if sort_value in x_sort:
                    sorted_content[sort_value].append(item.get("contents"))
                else:
                    x_sort.append(sort_value)
                    sorted_content.setdefault(sort_value, [item.get("contents")])
        return sorted_content

    def sort_queryset_by_month(self, queryset, x_label_key, year_range):
        x_sort = []
        sorted_content = {}
        for year in year_range:
            for month in range(1, 13):
                sort_value = f"{year}-{month}"
                if x_label_key["key"] == "create_at":
                    each_month_queryset = queryset.filter(
                        create_at__year=year, create_at__month=month
                    )
                if x_label_key["key"] == "update_at":
                    each_month_queryset = queryset.filter(
                        update_at__year=sort_value, update_at__month=month
                    )

                for item in each_month_queryset:
                    content = (
                        json.loads(item.contents)
                        if isinstance(item.contents, str)
                        else item.contents
                    )

                    # 2021-10-1
                    if sort_value in x_sort:
                        sorted_content[sort_value].append(content)
                    else:
                        x_sort.append(sort_value)
                        sorted_content.setdefault(sort_value, [content])
        return sorted_content

    def sort_queryset_by_year(self, queryset, x_label_key, year_range):
        x_sort = []
        sorted_content = {}

        for year in year_range:
            sort_value = f"{year}"

            if x_label_key["key"] == "create_at":
                each_year_queryset = queryset.filter(
                    create_at__year=year,
                )
            if x_label_key["key"] == "update_at":
                each_year_queryset = queryset.filter(
                    update_at__year=year,
                )

                # 2020/2021

            for item in each_year_queryset:
                content = (
                    json.loads(item.contents)
                    if isinstance(item.contents, str)
                    else item.contents
                )

                # 2021-10-1
                if sort_value in x_sort:
                    sorted_content[sort_value].append(content)
                else:
                    x_sort.append(sort_value)
                    sorted_content.setdefault(sort_value, [content])
        return sorted_content
