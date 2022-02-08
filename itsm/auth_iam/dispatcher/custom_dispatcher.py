# -*- coding: utf-8 -*-
import json

from django.views.decorators.csrf import csrf_exempt

from iam.contrib.django.dispatcher import (
    DjangoBasicResourceApiDispatcher,
    InvalidPageException,
)
from iam.contrib.django.dispatcher.dispatchers import (
    fail_response,
    logger,
    success_response,
)
from iam.contrib.django.dispatcher.exceptions import KeywordTooShortException
from iam.resource.utils import get_filter_obj, get_page_obj


class BaseDispatcher(DjangoBasicResourceApiDispatcher):
    def as_view(self, decorators=[]):
        @csrf_exempt
        def view(request):
            project_key = request.GET.get("project_key")
            worksheet_key = request.GET.get("worksheet_key")
            logger.info("request_get is {}".format(request.GET))

            provider = self._provider[self.get_resource_type()]
            provider.project_key = project_key
            provider.worksheet_key = worksheet_key
            return self._dispatch(request)

        for dec in decorators:
            view = dec(view)

        return view

    def get_resource_type(self):
        return None

    def _dispatch(self, request):
        request_id = request.META.get("HTTP_X_REQUEST_ID", "")

        # auth check
        # auth = request.META.get("HTTP_AUTHORIZATION", "")
        # auth_allowed = self.iam.is_basic_auth_allowed(self.system, auth)
        #
        # if not auth_allowed:
        #     logger.error(
        #         "resource request({}) auth failed with auth param: {}".format(
        #             request_id, auth
        #         )
        #     )
        #     return fail_response(401, "basic auth failed", request_id)

        # load json data
        try:
            data = json.loads(request.body)
        except Exception:
            logger.error(
                "resource request({}) failed with invalid body: {}".format(
                    request_id, request.body
                )
            )
            return fail_response(400, "reqeust body is not a valid json", request_id)

        # check basic params
        method = data.get("method")
        resource_type = self.get_resource_type()
        if not (method and resource_type):
            logger.error(
                "resource request({}) failed with invalid data: {}".format(
                    request_id, data
                )
            )
            return fail_response(400, "method and type is required field", request_id)

        # check resource type
        if resource_type not in self._provider:
            logger.error(
                "resource request({}) failed with unsupport resource type: {}".format(
                    request_id, resource_type
                )
            )
            return fail_response(
                404, "unsupport resource type: {}".format(resource_type), request_id
            )

        # check method and process
        processor = getattr(self, "_dispatch_{}".format(method), None)
        if not processor:
            logger.error(
                "resource request({}) failed with unsupport method: {}".format(
                    request_id, method
                )
            )
            return fail_response(404, "unsupport method: {}".format(method), request_id)

        logger.info(
            "resource request({}) with filter: {}, page: {}".format(
                request_id, data.get("filter"), data.get("page")
            )
        )
        try:
            return processor(request, data, request_id)
        except InvalidPageException as e:
            return fail_response(422, str(e), request_id)
        except Exception as e:
            logger.exception(
                "resource request({}) failed with exception: {}".format(request_id, e)
            )
            return fail_response(500, str(e), request_id)

    def _dispatch_list_attr(self, request, data, request_id):
        options = self._get_options(request)

        provider = self._provider[data["type"]]

        pre_process = getattr(provider, "pre_list_attr", None)
        if pre_process and callable(pre_process):
            pre_process(**options)

        result = provider.list_attr(**options)

        return success_response(result.to_list(), request_id)

    def _dispatch_list_attr_value(self, request, data, request_id):
        options = self._get_options(request)

        filter_obj = get_filter_obj(data.get("filter"), ["attr", "keyword", "ids"])
        page_obj = get_page_obj(data.get("page"))

        provider = self._provider[data["type"]]

        pre_process = getattr(provider, "pre_list_attr_value", None)
        if pre_process and callable(pre_process):
            pre_process(filter_obj, page_obj, **options)

        result = provider.list_attr_value(filter_obj, page_obj, **options)

        return success_response(result.to_dict(), request_id)

    def _dispatch_list_instance(self, request, data, request_id):
        options = self._get_options(request)

        filter_obj = get_filter_obj(
            data.get("filter"), ["parent", "search", "resource_type_chain"]
        )
        page_obj = get_page_obj(data.get("page"))

        provider = self._provider[self.get_resource_type()]

        pre_process = getattr(provider, "pre_list_instance", None)
        if pre_process and callable(pre_process):
            pre_process(filter_obj, page_obj, **options)

        result = provider.list_instance(filter_obj, page_obj, **options)

        return success_response(result.to_dict(), request_id)

    def _dispatch_fetch_instance_info(self, request, data, request_id):
        options = self._get_options(request)

        filter_obj = get_filter_obj(data.get("filter"), ["ids", "attrs"])

        provider = self._provider[data["type"]]

        pre_process = getattr(provider, "pre_fetch_instance_info", None)
        if pre_process and callable(pre_process):
            pre_process(filter_obj, **options)

        result = provider.fetch_instance_info(filter_obj, **options)

        return success_response(result.to_list(), request_id)

    def _dispatch_list_instance_by_policy(self, request, data, request_id):
        options = self._get_options(request)

        filter_obj = get_filter_obj(data.get("filter"), ["expression"])
        page_obj = get_page_obj(data.get("page"))

        provider = self._provider[data["type"]]

        pre_process = getattr(provider, "pre_list_instance_by_policy", None)
        if pre_process and callable(pre_process):
            pre_process(filter_obj, page_obj, **options)

        result = provider.list_instance_by_policy(filter_obj, page_obj, **options)

        return success_response(result.to_list(), request_id)

    def _dispatch_search_instance(self, request, data, request_id):
        options = self._get_options(request)

        filter_obj = get_filter_obj(data.get("filter"), ["parent", "keyword"])

        if filter_obj.keyword is None or len(filter_obj.keyword) < 2:
            raise KeywordTooShortException(
                "the length of keyword should be greater than or equals to 2"
            )

        page_obj = get_page_obj(data.get("page"))

        provider = self._provider[data["type"]]

        pre_process = getattr(provider, "pre_search_instance", None)
        if pre_process and callable(pre_process):
            pre_process(filter_obj, page_obj, **options)

        search_function = getattr(provider, "search_instance", None)
        if not (search_function and callable(search_function)):
            return fail_response(
                404,
                "resource type: {} not support search instance".format(data["type"]),
                request_id,
            )

        result = provider.search_instance(filter_obj, page_obj, **options)

        return success_response(result.to_dict(), request_id)


class WorksheetDispatcher(BaseDispatcher):
    def get_resource_type(self):
        return "worksheet"


class PageDispatcher(BaseDispatcher):
    def get_resource_type(self):
        return "page"
