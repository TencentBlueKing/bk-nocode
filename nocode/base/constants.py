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

# 常规字段长度定义
from nocode.utils.tools import ConstantDict

LEN_SHORT = 32
LEN_NORMAL = 64
LEN_MIDDLE = 128
LEN_LONG = 255
LEN_X_LONG = 1000
LEN_XX_LONG = 10000
LEN_XXX_LONG = 20000

EMPTY_INT = 0
EMPTY_STRING = ""
EMPTY_DISPLAY_STRING = "--"
EMPTY_LIST = []
EMPTY_VARIABLE = {"inputs": [], "outputs": []}
DEFAULT_BK_BIZ_ID = -1
EMPTY = "EMPTY"
EMPTY_DICT = ConstantDict({})

TYPE_CHOICES = [
    ("STRING", "单行文本"),
    ("TEXT", "多行文本"),
    ("INT", "数字"),
    ("DATE", "日期"),
    ("DATETIME", "时间"),
    ("DATETIMERANGE", "时间间隔"),
    ("TABLE", "表格"),
    ("SELECT", "单选下拉框"),
    ("INPUTSELECT", "可输入单选下拉框"),
    ("MULTISELECT", "多选下拉框"),
    ("CHECKBOX", "复选框"),
    ("RADIO", "单选框"),
    ("MEMBER", "单选人员选择"),
    ("MEMBERS", "多选人员选择"),
    ("RICHTEXT", "富文本"),
    ("FILE", "附件上传"),
    ("CUSTOMTABLE", "自定义表格"),
    ("TREESELECT", "树形选择"),
    ("LINK", "链接"),
    ("CUSTOM-FORM", "自定义表单"),
    ("CASCADE", "级联"),
    ("AUTO-NUMBER", "自动编号"),
    # 新增图片控件
    ("IMAGE", "图片上传"),
    ("FORMULA", "公式控件"),
]

IGNORE_FIELDS_TYPE = ["FORMULA"]
SELECT_FIELDS_TYPE = ["SELECT", "INPUTSELECT", "MULTISELECT", "CHECKBOX", "RADIO"]

LOG_EXPIRE_DAYS = 30

FORMULA = "FORMULA"
CUSTOM = "CUSTOM"
SUM = "SUM"
MAX = "MAX"
MIN = "MIN"
AVERAGE = "AVERAGE"
PRODUCT = "PRODUCT"

CALCULATE_LIMIT = 1

FORMULA_BUILTIN = [
    ("SUM", "求和"),
    ("MAX", "最大值"),
    ("MIN", "最小值"),
    ("AVERAGE", "均值"),
    ("PRODUCT", "乘积"),
    ("CUSTOM", "自定义"),
    ("COUNT", "计数"),
    ("MEDIAN", "中位数"),
    ("ARGMAX", "众数"),
]

TIME_RANGE_BUILTIN = ["CURRENT_WEEK", "CURRENT_MONTH", "CURRENT_YEAR", "DEFINE"]

LAYOUT_CHOICES = [
    ("COL_6", "半行"),
    ("COL_12", "整行"),
]

VALIDATE_CHOICES = [
    ("OPTION", "可选"),
    ("REQUIRE", "必填"),
]

SOURCE_CHOICES = [
    ("CUSTOM", "自定义数据"),
    ("API", "接口数据"),
    ("DATADICT", "数据字典"),
    ("RPC", "系统数据"),
    ("WORKSHEET", "工作表"),
]

DEFAULT_PROJECT_PROJECT_KEY = "0"
PUBLIC_PROJECT_PROJECT_KEY = "public"

ROOT_ORDER = 0
DEFAULT_ORDER = 1

# 开始序号
FIRST_ORDER = 1

# role
CMDB = "CMDB"
GENERAL = "GENERAL"
OPEN = "OPEN"
PERSON = "PERSON"
STARTER = "STARTER"
STARTER_LEADER = "STARTER_LEADER"
BY_ASSIGNOR = "BY_ASSIGNOR"
ORGANIZATION = "ORGANIZATION"
VARIABLE = "VARIABLE"
INVISIBLE = "INVISIBLE"
IAM = "IAM"
API = "API"
ASSIGN_LEADER = "ASSIGN_LEADER"
MANAGER = "MANAGER"

ONLY_MANAGER = 1

# 服务展示使用
DISPLAY_CHOICES = [
    (CMDB, "CMDB业务公用角色"),
    (GENERAL, "通用角色表"),
    (OPEN, "不限"),
    (PERSON, "个人"),
    (ORGANIZATION, "组织架构"),
    (INVISIBLE, "不可见"),
    (API, "第三方系统"),
]

# CACHE
CACHE_5MIN = 5 * 60
CACHE_10MIN = 10 * 60
CACHE_30MIN = 30 * 60
CACHE_1H = 1 * 60 * 60

# project_manager_operate
PROJECT_MANAGER_ADD = "ADD"
PROJECT_MANAGER_DELETE = "DELETE"
OPERATES = [PROJECT_MANAGER_ADD, PROJECT_MANAGER_DELETE]

FILE_PATH = "/data/app/code/USERRES/"

WORKSHEET = "WORKSHEET"
FUNCTION = "FUNCTION"

FUNCTION_CARD = {
    "page_id": "",
    "type": "FUNCTION",
    "value": 0,
}

LINK_CARD = {
    "page_id": "",
    "type": "LINK",
    "value": 0,
}

PAGE_TYPE_CHOICES = [
    ("FUNCTION", "功能卡片"),
    ("LIST", "列表"),
    ("SHEET", "表单"),
    ("CHART", "图表"),
    ("GROUP", "分组"),
    ("CUSTOM", "自定义"),
]

PAGE_COMPONENT_TYPE_CHOICES = [
    ("FUNCTION", "功能组件"),
    ("FUNCTION_GROUP", "功能组"),
    ("LIST", "列表组件"),
    ("SHEET", "表单组件"),
    ("CHART", "图表"),
    ("RICHTEXT", "图文"),
    ("LINK", "链接组件"),
    ("LINK_GROUP", "外部链接组"),
    ("TAB", "选项卡"),
]
