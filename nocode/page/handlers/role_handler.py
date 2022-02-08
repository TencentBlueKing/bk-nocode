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


from itsm.role.models import UserRole
from nocode.base.base_handler import APIModel


class RoleHandler(APIModel):
    def __init__(self, role_type=None, instance=None, **kwargs):
        self.role_type = role_type
        self.obj = instance
        self.kwarg = kwargs
        super(RoleHandler, self).__init__()

    def _get_instance(self):
        try:
            if self.role_type is None:
                obj = UserRole.objects.get(**self.kwarg)
            else:
                obj = UserRole.objects.get(role_type=self.role_type)
            return obj
        except UserRole.DoesNotExist:
            return None

    @classmethod
    def get_users_by_role(cls, display_type, display_role, project_key):
        return UserRole.objects.filter(
            role_type=display_type, role_key=display_role, project_key=project_key
        ).values_list("members", flat=True)

    @classmethod
    def get_general_role_by_user(cls, username):
        return UserRole.objects.filter(members__contains=username).values_list(
            "role_type", "role_key"
        )

    @classmethod
    def get_users_by_type(cls, display_type, display_role):
        return UserRole.get_users_by_type(
            bk_biz_id=0, user_type=display_type, users=display_role
        )

    @classmethod
    def get_group(cls, display_type, role_key, project_key=None):
        return UserRole.objects.get(
            role_type=display_type, role_key=role_key, project_key=project_key
        )
