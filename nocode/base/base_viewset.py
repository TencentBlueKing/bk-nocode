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
from rest_framework.viewsets import GenericViewSet

from nocode.base.module_handler import ModelViewSet, APIViewSet, ReadOnlyModelViewSet


def custom_params_valid(serializer, params, many=False):
    _serializer = serializer(data=params, many=many)
    _serializer.is_valid(raise_exception=True)
    if many:
        return list(_serializer.data)
    else:
        return dict(_serializer.data)


class ValidationMixin(GenericViewSet):
    def params_valid(self, serializer, params=None):
        """
        校验参数是否满足 serializer 规定的格式，支持传入serializer
        """
        # 校验request中的参数
        if not params:
            if self.request.method in ["GET"]:
                params = self.request.query_params
            else:
                params = self.request.data

        return custom_params_valid(serializer=serializer, params=params)

    @property
    def validated_data(self):
        """
        校验的数据
        """
        # 优先使用缓存，避免多次取值时重复序列化和校验
        cache_validated_data = getattr(self, "cache_validated_data", None)
        if cache_validated_data:
            return cache_validated_data

        if self.request.method == "GET":
            data = self.request.query_params
        else:
            data = self.request.data
        serializer = self.serializer_class or self.get_serializer_class()
        cache_validated_data = self.params_valid(serializer, data)
        setattr(self, "cache_validated_data", cache_validated_data)
        return cache_validated_data


class BaseModelViewSet(ModelViewSet, ValidationMixin):
    pass


class BaseApiViewSet(APIViewSet, ValidationMixin):
    pass


class BaseReadOnlyViewSet(ValidationMixin, ReadOnlyModelViewSet):
    pass
