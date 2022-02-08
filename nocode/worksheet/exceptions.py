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


class WorkSheetDoesNotExist(ServerError):
    MESSAGE = _("工作表不存在")
    ERROR_CODE = "WorkSheet Does Not Exist"
    ERROR_CODE_INT = 4000001


class WorkSheetFieldDoesNotExist(ServerError):
    MESSAGE = _("工作表字段不存在")
    ERROR_CODE = "WorkSheetField Does Not Exist"
    ERROR_CODE_INT = 4000002


class CreateWorkSheetError(ServerError):
    MESSAGE = _("工作表创建失败")
    ERROR_CODE = "Create WorkSheet Error"
    ERROR_CODE_INT = 4000003


class DropUniqueIndexError(ServerError):
    MESSAGE = _("唯一性索引删除失败")
    ERROR_CODE = "Drop Unique Index Error"
    ERROR_CODE_INT = 4000004


class CreateUniqueIndexError(ServerError):
    MESSAGE = _("唯一性索引创建失败")
    ERROR_CODE = "Create Unique Index Error"
    ERROR_CODE_INT = 4000005


class FormulaInputError(ServerError):
    MESSAGE = _("数值输入无法计算")
    ERROR_CODE = "Can`t calculate this matter"
    ERROR_CODE_INT = 4000006


class NotSupportExcelFileType(ServerError):
    MESSAGE = _("不支持的Excel文件类型")
    ERROR_CODE = "Not support excel file type"
    ERROR_CODE_INT = 4000007


class InitWorkSheetError(ServerError):
    MESSAGE = _("初始化工作表错误")
    ERROR_CODE = "Init WorkSheet Error"
    ERROR_CODE_INT = 4000008
