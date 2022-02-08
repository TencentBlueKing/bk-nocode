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
import json
import os
import sys
import inspect
from functools import wraps
from typing import List, Dict, Tuple

from django.test import TestCase, Client, override_settings
from drf_spectacular.generators import EndpointEnumerator
from mock import patch
from rest_framework import status

JSON_CONTENT = "application/json"

OVERRIDE_MIDDLEWARE = "itsm.tests.middlewares.OverrideMiddleware"


class ObjectBase(object):
    META = {}
    COOKIES = {}


MOCK_REQUEST_OBJECT = ObjectBase()


class EndPointIndex:
    PATH = 0
    PATTERN = 1
    METHOD = 2
    ACTION_FUNC = 3


class ActionFuncIndex:
    # action指定url_path时方法名称不为path
    FUNC_NAME = 0
    FUNC = 1


class MyTestClient(Client):
    @staticmethod
    def check_environ():
        to_check_var = [
            "APP_CODE",
            "APP_TOKEN",
            "BK_PAAS_HOST",
            "PAAS_ADMIN_USER",
            "PAAS_ADMIN_PASS",
        ]
        for var in to_check_var:
            if not os.environ.get(var):
                raise NotImplementedError(f"环境变量{var}未设置")

    @staticmethod
    def assert_response(response):
        """
        断言请求是否正确返回
        :param response:
        :return: 返回数据中的data字段
        """
        assert response.status_code == 200
        json_response = json.loads(response.content)
        try:
            assert json_response.get("result")
        except AssertionError as error:
            print("[RESPONSE ERROR]: {}".format(response.content))
            raise error

        return json_response["data"]

    @staticmethod
    def transform_data(data, content_type=JSON_CONTENT):
        """
        根据content_type转化请求参数
        :param data:
        :param content_type:
        :return:
        """
        if content_type == JSON_CONTENT:
            data = json.dumps(data)
        return data

    def get(self, path, data=None, secure=True, **extra):
        response = super(MyTestClient, self).get(
            path, data=data, secure=secure, **extra
        )

        return self.assert_response(response)

    def post(
        self,
        path,
        data=None,
        content_type=JSON_CONTENT,
        follow=False,
        secure=True,
        **extra,
    ):
        data = self.transform_data(data, content_type)
        response = super(MyTestClient, self).post(
            path,
            data=data,
            content_type=JSON_CONTENT,
            follow=follow,
            secure=secure,
            **extra,
        )
        return self.assert_response(response)

    def patch(
        self,
        path,
        data=None,
        content_type=JSON_CONTENT,
        follow=False,
        secure=True,
        **extra,
    ):
        data = self.transform_data(data, content_type)
        response = super(MyTestClient, self).patch(
            path,
            data=data,
            content_type=JSON_CONTENT,
            follow=follow,
            secure=secure,
            **extra,
        )
        return self.assert_response(response)

    def put(
        self,
        path,
        data=None,
        content_type=JSON_CONTENT,
        follow=False,
        secure=True,
        **extra,
    ):
        data = self.transform_data(data, content_type)
        response = super(MyTestClient, self).put(
            path,
            data=data,
            content_type=JSON_CONTENT,
            follow=follow,
            secure=secure,
            **extra,
        )
        return self.assert_response(response)

    def delete(
        self,
        path,
        data=None,
        content_type=JSON_CONTENT,
        follow=False,
        secure=True,
        **extra,
    ):
        data = self.transform_data(data, content_type)
        response = super(MyTestClient, self).delete(
            path,
            data=data,
            content_type=JSON_CONTENT,
            follow=follow,
            secure=secure,
            **extra,
        )
        return self.assert_response(response)


class Action:
    def __init__(self, request_method: str, action_name: str, request_path: str = None):
        """
        :param request_method: 接口请求方法
        :param action_name: 接口名称（后缀）
        :param request_path: 接口请求路径
        """
        self.request_method = request_method.lower()
        self.action_name = action_name
        self.request_path = request_path

        self._params = None
        self._response = None

    def __str__(self):
        return f"<{self.action_name}: {self.request_method}> - {self.request_path}"

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, params: Dict):
        self._params = params

    @property
    def response(self):
        return self._response

    @response.setter
    def response(self, response: [List, Dict]):
        self._response = response


def assert_handler(action: Action):
    def assert_handler_inner(test_method):
        @wraps(test_method)
        def wrapper(inst, *args, **kwargs):
            try:
                test_method(inst, *args, **kwargs)
            except AssertionError:
                sys.stdout.write(
                    "[×] 「{component}」 {action}\n".format(
                        component=inst.__class__.__name__, action=action
                    )
                )
                raise
            else:
                sys.stdout.write(
                    "[√] 「{component}」 {action}\n".format(
                        component=inst.__class__.__name__, action=action
                    )
                )

        return wrapper

    return assert_handler_inner


class SwaggerViewSetTestMetaClass(type):
    base_action = {
        "list": "get",
        "create": "post",
        "retrieve": "get",
        "update": "put",
        "partial_update": "patch",
        "destroy": "delete",
    }

    def __new__(mcs, name, bases, attrs):
        """
        :param name: 类名称
        :param bases: 类继承的父类集合
        :param attrs: 类的方法集合
        """
        return type.__new__(mcs, name, bases, attrs)

    def __init__(cls, *args, **kwargs):
        if cls.swagger_test_view is None:
            super().__init__(*args, **kwargs)
            return
        action_func_tuples = cls.view_action_func_tuples(cls.swagger_test_view)
        action_list = cls.action_list(cls.swagger_test_view)

        action_name_func_map = {
            cls.func_action(action_func_tuple).action_name: action_func_tuple[
                ActionFuncIndex.FUNC
            ]
            for action_func_tuple in action_func_tuples
        }

        for action in action_list:
            if action.action_name not in action_name_func_map:
                sys.stdout.write(f"生成测试缺少：{action}\n")
                continue
            if action.action_name in cls.actions_exempt:
                sys.stdout.write(f"skip：{action}\n")
                continue
            cls.fill_mock_data_to_action(
                action, action_name_func_map[action.action_name]
            )
            setattr(
                cls, f"test_{action.action_name}_auto", cls.generator_test_func(action)
            )

        super().__init__(*args, **kwargs)

    @classmethod
    def generator_test_func(mcs, action: Action, *args, **kwargs):
        @assert_handler(action)
        @override_settings(MIDDLEWARE=(OVERRIDE_MIDDLEWARE,))
        def test_method(inst):
            response = getattr(inst.client, action.request_method)(
                path=action.request_path.format(**inst.path_params), data=action.params
            )
            try:
                inst.assertExemptDataStructure(response, action.response, value_eq=True)
            except AssertionError:
                sys.stdout.write(f"result: {json.dumps(response, indent=4)}\n")
                sys.stdout.write(f"except: {json.dumps(action.response, indent=4)}\n")
                raise

        return test_method

    @staticmethod
    def action_list(view) -> List[Action]:
        action_list = []
        for endpoint in EndpointEnumerator().get_api_endpoints():
            if endpoint[EndPointIndex.ACTION_FUNC].cls != view:
                continue
            method_lower = endpoint[EndPointIndex.METHOD].lower()
            action_name = endpoint[EndPointIndex.ACTION_FUNC].actions[method_lower]
            action_list.append(
                Action(
                    request_path=endpoint[EndPointIndex.PATH],
                    request_method=method_lower,
                    action_name=action_name,
                )
            )
        return action_list

    @classmethod
    def fill_mock_data_to_action(mcs, action: Action, action_func) -> None:
        try:
            swagger_auto_schema = action_func._swagger_auto_schema
            if action.action_name not in mcs.base_action:
                swagger_auto_schema = swagger_auto_schema[action.request_method]

            if action.request_method in ["get", "delete"]:
                action.params = swagger_auto_schema[
                    "query_serializer"
                ].Meta.swagger_schema_fields["example"]
            else:
                action.params = swagger_auto_schema[
                    "request_body"
                ].Meta.swagger_schema_fields["example"]

        except Exception:
            action.params = {}

        try:
            swagger_auto_schema = action_func._swagger_auto_schema
            if action.action_name not in mcs.base_action:
                swagger_auto_schema = swagger_auto_schema[action.request_method]
            # TODO 目前只测试成功响应
            action.response = (
                swagger_auto_schema["responses"]
                .get(status.HTTP_200_OK)
                .Meta.swagger_schema_fields["example"]
            )
        except Exception:
            pass

    @classmethod
    def func_action(mcs, action_func_tuple: Tuple) -> Action:
        if action_func_tuple[ActionFuncIndex.FUNC_NAME] in mcs.base_action:
            return Action(
                request_method=mcs.base_action[
                    action_func_tuple[ActionFuncIndex.FUNC_NAME]
                ],
                action_name=action_func_tuple[ActionFuncIndex.FUNC_NAME],
            )
        action_func = action_func_tuple[ActionFuncIndex.FUNC]
        # TODO 暂不考虑一个接口有多种请求方式
        request_method, action_name = list(action_func.mapping.items())[0]
        return Action(request_method=request_method, action_name=action_name)

    @classmethod
    def is_action_func_tuple(mcs, func_tuple: Tuple) -> bool:
        func = func_tuple[ActionFuncIndex.FUNC]
        if func_tuple[ActionFuncIndex.FUNC_NAME] in mcs.base_action or hasattr(
            func, "url_path"
        ):
            return True
        return False

    @classmethod
    def view_action_func_tuples(mcs, view) -> List[Tuple]:
        return [
            func
            for func in inspect.getmembers(view, predicate=inspect.isfunction)
            if mcs.is_action_func_tuple(func)
        ]


class MyTestCase(TestCase, metaclass=SwaggerViewSetTestMetaClass):
    # None表示展示全量断言差异
    maxDiff = None

    client_class = MyTestClient
    client = MyTestClient()

    # 默认的测试业务
    pk = 1

    # swagger文档自动化测试相关
    # 不为None时，自动生成并执行指定viewset接口单测
    swagger_test_view = None
    path_params = {"pk": pk}
    fields_exempt = ["created_at", "updated_at"]
    actions_exempt = []

    # 断言相关
    recursion_type = [dict, list]
    string_type = [str]

    def remove_keys(self, data, keys: List[str]) -> None:
        children = []
        if isinstance(data, dict):
            for key in keys:
                data.pop(key, None)
            children = data.values()
        elif isinstance(data, list):
            children = data
        for child_data in children:
            if type(child_data) in self.recursion_type:
                self.remove_keys(child_data, keys)
        return

    def assertExemptDataStructure(
        self, result_data, expected_data, value_eq=False, list_exempt=False
    ):
        self.remove_keys(result_data, self.fields_exempt)
        self.remove_keys(expected_data, self.fields_exempt)
        return self.assertDataStructure(
            result_data, expected_data, value_eq, list_exempt, is_sort=False
        )

    def assertDataStructure(
        self,
        result_data,
        expected_data,
        value_eq=False,
        list_exempt=False,
        is_sort=True,
    ):
        """
        将数据的结构以及类型进行断言验证
        :param result_data: 后台返回的数据
        :param expected_data: 希望得到的数据
        :param value_eq: 是否对比值相等
        :param list_exempt: 是否豁免列表的比对
        :param is_sort: 是否对列表（子列表）在对比前排序
        """
        result_data_type = type(result_data)

        # 判断类型是否一致
        self.assertEqual(result_data_type, type(expected_data))

        # 判断类型是否为字典
        if result_data_type is dict:
            # 將传入的预给定信息，将键值分别取出
            for expected_key, expected_value in list(expected_data.items()):
                # 判断键是否存在
                self.assertTrue(
                    expected_key in list(result_data.keys()),
                    msg="key:[%s] is expected" % expected_key,
                )

                result_value = result_data[expected_key]

                # 返回None时忽略 @todo一刀切需要调整
                if expected_value is None or result_value is None:
                    return

                # 取出后台返回的数据result_data，判断是否与给定的类型相符
                result_value_type = type(result_value)
                expected_value_type = type(expected_value)
                self.assertEqual(
                    result_value_type,
                    expected_value_type,
                    msg="type error! Expect [%s] to be [%s], but got [%s]"
                    % (expected_key, expected_value_type, result_value_type),
                )

                if value_eq:
                    self.assertEqual(result_value, expected_value)

                # 判断该类型是否为字典或者列表
                if expected_value_type in self.recursion_type:
                    # 进行递归
                    self.assertDataStructure(
                        result_value,
                        expected_value,
                        value_eq=value_eq,
                        list_exempt=list_exempt,
                        is_sort=is_sort,
                    )

        #  判断类型是否为列表
        elif result_data_type is list:
            # 列表不为空且不进行列表比对的豁免
            if not list_exempt:

                if value_eq:
                    # 比对列表内的值是否相等
                    self.assertListEqual(result_data, expected_data, is_sort=is_sort)
                else:
                    # 否则认为列表里所有元素的数据结构都是一致的
                    _expected_data = expected_data[0]
                    for _data in result_data:
                        if type(_data) in self.recursion_type:
                            self.assertDataStructure(
                                _data,
                                _expected_data,
                                value_eq=value_eq,
                                list_exempt=list_exempt,
                                is_sort=is_sort,
                            )

        # 判断值是否一致
        elif value_eq:
            self.assertEqual(result_data, expected_data)

    def assertListEqual(self, list1, list2, msg=None, is_sort=False):
        if is_sort:
            # TODO 没有考虑Dict类型的排序
            list1.sort()
            list2.sort()
        super(MyTestCase, self).assertListEqual(list1, list2, msg=msg)

    def setUp(self) -> None:
        """执行TestCase内test时调用一次"""
        super(MyTestCase, self).setUp()

    def tearDown(self) -> None:
        """执行TestCase内test后调用一次"""
        super(MyTestCase, self).tearDown()

    @classmethod
    def setUpTestData(cls):
        """TestCase实例生成时调用一次, 可DB回滚
        该hook比setUpClass先执行，需要考虑mock相关顺序
        """
        super().setUpTestData()

    @classmethod
    def setUpClass(cls):
        """TestCase实例生成时调用一次"""
        super(MyTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        """TestCase实例销毁时调用一次"""
        super(MyTestCase, cls).tearDownClass()
        patch.stopall()
