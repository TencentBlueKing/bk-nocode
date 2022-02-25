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
import json
import uuid

from django.db.models import Q
from django.utils.decorators import method_decorator
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.response import Response

from blueapps.account.decorators import login_exempt

from config.default import TOKEN_EXPIRE_TIME
from itsm.project.handler.project_handler import ProjectHandler
from itsm.service.validators import service_validate
from itsm.ticket.models import Ticket, TicketEventLog
from itsm.ticket.serializers import TicketSerializer, EventSerializer
from itsm.ticket.tasks import start_pipeline
from nocode.base.base_viewset import BaseApiViewSet
from nocode.base.module_handler import ReadOnlyModelViewSet
from nocode.data_engine.handlers.data_handler import (
    ListComponentDataHandler,
    WorkSheetDataHandler,
    ChartDataHandler,
)
from nocode.data_engine.serializers import query
from nocode.openapi.handlers.moudule_handler import AUTH_META
from nocode.openapi.serializers.project_serializer import ProjectSerializer
from nocode.page.exceptions import OpenLinkVerifyError
from nocode.project_manager.handlers.open_link_handler import OpenLinkVerifyHandler
from nocode.project_manager.handlers.project_version_handler import (
    ProjectVersionModelHandler,
)

DataInstanceViewTags = ["openapi_data_instance"]
store = settings.STORE


@method_decorator(login_exempt, name="dispatch")
class DataInstanceViewSet(BaseApiViewSet):
    @swagger_auto_schema(
        operation_summary="获取某个列表组件的数据",
        tags=DataInstanceViewTags,
        request_body=query.ListComponentSerializers(),
    )
    @action(
        detail=False, methods=["post"], serializer_class=query.ListComponentSerializers
    )
    def list_component_data(self, request, *args, **kwargs):
        conditions = self.validated_data.get("conditions", {})
        version_number = self.validated_data.get("version_number", None)
        page_component_id = self.validated_data["page_id"]
        return ListComponentDataHandler(
            page_component_id, request, version_number
        ).get_list_components_data(conditions, need_page=False)

    @swagger_auto_schema(
        operation_summary="导出某个列表组件的数据",
        tags=DataInstanceViewTags,
        request_body=query.ListComponentSerializers(),
    )
    @action(
        detail=False, methods=["post"], serializer_class=query.ListComponentSerializers
    )
    def export_list_component_data(self, request, *args, **kwargs):
        # 没有ids默认获取全部记录
        ids = self.validated_data.get("ids", [])
        conditions = self.validated_data.get("conditions", {})
        page_id = self.validated_data["page_id"]
        version_number = self.validated_data.get("version_number", None)
        return ListComponentDataHandler(
            page_id, request, version_number
        ).export_list_component_data(conditions=conditions, ids=ids)

    @swagger_auto_schema(
        operation_summary="根据筛选条件获取列表的数据",
        tags=DataInstanceViewTags,
        request_body=query.WorkSheetSerializers(),
    )
    @action(detail=False, methods=["post"], serializer_class=query.WorkSheetSerializers)
    def worksheet_data(self, request, *args, **kwargs):
        token = self.validated_data.get("token")
        if not token:
            return Response()
        data_config_bytes = settings.REDIS_INST.get(token)
        data_config = json.loads(data_config_bytes)
        settings.REDIS_INST.delete(token)

        conditions = self.validated_data.get("conditions", {})
        worksheet_id = data_config["target"]["worksheet_id"]
        fields = self.validated_data["fields"]
        need_page = self.validated_data["need_page"]
        data = WorkSheetDataHandler(worksheet_id, request).data(
            conditions, fields, need_page
        )
        if need_page:
            return data

        return Response(data)

    @swagger_auto_schema(
        operation_summary="获取某个图表页面的数据回馈",
        tags=DataInstanceViewTags,
        request_body=query.ChartComponentDataSerializer(),
    )
    @action(
        detail=False,
        methods=["post"],
        serializer_class=query.ChartComponentDataSerializer,
    )
    def list_chart_data(self, request, *args, **kwargs):
        chart_configs = self.validated_data["chart_configs"]
        data = ChartDataHandler(
            request=request,
        ).analysis(chart_configs)
        return Response(data)

    @swagger_auto_schema(
        operation_summary="获取某个版本下某个表单的数据回馈",
        tags=DataInstanceViewTags,
        serializer_class=query.WorkSheetVersionSerializers(),
    )
    @action(
        detail=False,
        methods=["get"],
        serializer_class=query.WorkSheetVersionSerializers,
    )
    def get_worksheet_data(self, request, *args, **kwargs):
        version_number = self.validated_data["version_number"]
        worksheet_id = self.validated_data["worksheet_id"]

        queryset = WorkSheetDataHandler(
            worksheet_id=worksheet_id, request=request
        ).get_worksheet_data_by_version(version_number)

        return Response(queryset)

    @swagger_auto_schema(
        operation_summary="获取某个版本应用下表单",
        tags=DataInstanceViewTags,
    )
    @action(
        detail=False,
        methods=["get"],
    )
    def get_worksheet(self, request, *args, **kwargs):
        version_number = request.query_params.get("version_number")
        project_key = request.query_params.get("project_key")

        version = ProjectVersionModelHandler(
            project_key=project_key, version_number=version_number
        ).instance
        worksheets = version.worksheet
        return Response(worksheets)

    @swagger_auto_schema(
        operation_summary="获取用户下的应用",
        tags=DataInstanceViewTags,
        serializer_class=ProjectSerializer(),
    )
    @action(
        detail=False,
        methods=["get"],
    )
    def get_user_project(self, request, *args, **kwargs):
        username = request.query_params.get("username")
        if not username:
            return Response()
        user_projects = ProjectHandler().all_project.filter(
            Q(owner__users__icontains=username) | Q(creator=username), is_deleted=False
        )
        serializer = ProjectSerializer(instance=user_projects, many=True)
        return Response(serializer.data)


@method_decorator(login_exempt, name="dispatch")
class TicketModelViewSet(BaseApiViewSet):
    @action(detail=False, methods=["get"])
    def get_first_state_fields(self, request, *args, **kwargs):
        """
        获取提单节点字段
        """
        token = request.query_params.get("token")
        if not token:
            raise OpenLinkVerifyError()
        service_id = OpenLinkVerifyHandler(token).get_service()

        # 获取对应的流程版本
        service, catalog_services = service_validate(service_id)
        field_ids = service.workflow.first_state["fields"]
        state_id = service.workflow.first_state["id"]

        fields = []
        for field_id in field_ids:
            version_field = service.workflow.get_field(field_id)
            # 忽略错误的id
            if version_field is None:
                continue

            field = copy.deepcopy(version_field)
            default = field.get("default")
            old_value = field.get("value")
            field.update(
                state_id=state_id,
                version_id=service.workflow.id,
                value=default if old_value is None else old_value,
            )
            # 如果可配置数据源类型的关联其他应用的表单，生成token，数据依据查询token
            if field["meta"].get("data_config"):
                # 生成uuid:data_config
                key = uuid.uuid4().hex
                value = json.dumps(field["meta"].get("data_config"))
                # token会过期，每次刷新都会刷新token
                settings.REDIS_INST.setex(key, TOKEN_EXPIRE_TIME, value)
                field.setdefault("token", key)
            else:
                field.setdefault("token", "")
            fields.append(field)

        return Response(fields)

    @swagger_auto_schema(
        operation_summary="提单",
        request_body=TicketSerializer(),
    )
    @action(detail=False, methods=["post"])
    def create_ticket(self, request, *args, **kwargs):
        """
        创建单据
        service_id: 服务id
        fields: 提单节点字段信息
        """
        # 创建单据
        data = copy.deepcopy(request.data)

        token = data.pop("token", "")
        if not token:
            raise OpenLinkVerifyError()
        service_id = OpenLinkVerifyHandler(token).get_service()
        data["service_id"] = service_id

        serializer = TicketSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        instance.do_after_create(
            data["fields"], request.data.get("from_ticket_id", None)
        )
        start_pipeline.apply_async([instance])
        return Response(
            {"sn": instance.sn, "id": instance.id, "ticket_url": instance.pc_ticket_url}
        )


@method_decorator(login_exempt, name="dispatch")
class EventLogViewSet(ReadOnlyModelViewSet):
    pagination_class = None
    queryset = TicketEventLog.objects.all().select_related("ticket")
    serializer_class = EventSerializer
    filter_fields = {
        "status": ["exact"],
        "type": ["exact", "in"],
        "from_state_id": ["exact"],
    }

    def get_queryset(self):
        """
        重写get_queryset
        :return:
        """
        queryset = super(EventLogViewSet, self).get_queryset()
        if not (
            self.request.query_params.get("ticket")
            and self.request.query_params.get("state")
        ):
            # 不存在的请求参数，直接返回空
            return queryset.none()
        state_id = self.request.query_params.get("state")
        ticket = Ticket.objects.get(id=self.request.query_params["ticket"])

        return queryset.filter(ticket=ticket, from_state_id=state_id)


@method_decorator(login_exempt, name="dispatch")
class SystemViewSet(BaseApiViewSet):
    @action(detail=False, methods=["get"])
    def meta(self, request):
        return Response(AUTH_META)
