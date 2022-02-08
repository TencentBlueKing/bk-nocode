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
import copy
import hashlib
from django.utils.crypto import get_random_string
from pypinyin.core import lazy_pinyin

from nocode.base.constants import IGNORE_FIELDS_TYPE


def get_random_key(name):
    """
    通过中文名生成英文key，并做md5转码返回
    若拼音解析失败，则生成随机key
    """

    try:
        word_list = lazy_pinyin(name)
    except BaseException:
        word_list = [get_random_string(3) for _ in range(3)]

    pinyin_key = "{}-{}".format(".".join(word_list), get_random_string(4))

    return hashlib.md5(pinyin_key.encode("utf-8")).hexdigest()


def check_user_owner_creator(user, project):
    owner = copy.deepcopy(project.owner)
    owner_list = owner.get("users", [])
    if owner_list is None:
        owner_list = []
    owner_list.append(project.creator)
    if user.username not in owner_list:
        return False
    return True


def ignore_fields_type(field_type):
    if field_type in IGNORE_FIELDS_TYPE:
        return True
    return False
