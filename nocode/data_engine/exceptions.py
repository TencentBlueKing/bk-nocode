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
from django.utils.translation import ugettext as _

from nocode.exceptions import ServerError


class PageComponentError(ServerError):
    MESSAGE = _("页面组件异常, 列表类型的页面只允许有一个页面组件")
    ERROR_CODE = "Page Component Not Exists"
    ERROR_CODE_INT = 4200001


class GetDetailDataError(ServerError):
    MESSAGE = _("获取页面数据详情数据异常")
    ERROR_CODE = "Get Detail Not Exists"
    ERROR_CODE_INT = 4200002


class ImportDataError(ServerError):
    MESSAGE = _("数据导入")
    ERROR_CODE = "Import Data Error"
    ERROR_CODE_INT = 4200003


class DataValidateError(ServerError):
    MESSAGE = _("数据校验失败")
    ERROR_CODE = "Data Validate Error"
    ERROR_CODE_INT = 4200004


class FileValidateError(ServerError):
    MESSAGE = _("文件校验失败，只支持excel文件")
    ERROR_CODE = "File Validate Error"
    ERROR_CODE_INT = 4200005
