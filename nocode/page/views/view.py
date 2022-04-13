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
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from itsm.component.drf.viewsets import NormalModelViewSet
from nocode.base.constants import DEFAULT_PROJECT_PROJECT_KEY, PERSON
from nocode.page.handlers.moudle_handler import ModelViewSet
from nocode.page.handlers.page_handler import (
    PageModelHandler,
    PageComponentHandler,
    PageComponentCollectionHandler,
    PageOpenLinkHandler,
)
from nocode.page.handlers.permission_handler import PageViewPermission
from nocode.page.models import Page, PageComponent, PageComponentCollection
from nocode.page.permission import PageComponentPermission
from nocode.page.serializers.serializers import (
    PageSerializer,
    PageComponentSerializer,
    PageShortcutSerializer,
    PageComponentListSerializer,
    PageListSerializer,
    PageDisplayByRole,
    PageMoveSerializer,
    BatchComponentsSerializer,
    PageComponentCollectionSerializer,
    SetShowModeListSerializer,
    GenerateOpenLinkSerializer,
    ClearOpenLinkSerializer,
)
from nocode.project_manager.handlers.module_handler import PageHandler


class PageModelViewSet(ModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    permission_classes = (PageViewPermission,)

    def perform_destroy(self, instance):
        """
        刪除页面，连带页面组件一起删除
        """
        PageComponent.objects.filter(page_id=instance.id).delete()
        super().perform_destroy(instance)

    @swagger_auto_schema(
        operation_summary="页面列表",
        query_serializer=PageListSerializer(),
    )
    def list(self, request, *args, **kwargs):
        project_key = request.query_params.get("project_key")
        if not project_key:
            return Response()

        serializer = PageListSerializer(data={"project_key": project_key})
        serializer.is_valid(raise_exception=True)

        self.queryset = self.queryset.filter(
            project_key=serializer.validated_data["project_key"]
        )
        return super(PageModelViewSet, self).list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="页面创建",
    )
    def create(self, request, *args, **kwargs):
        return super(PageModelViewSet, self).create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="获取单个页面详情",
    )
    def retrieve(self, request, *args, **kwargs):
        return super(PageModelViewSet, self).retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="页面导航分组",
    )
    @action(detail=False, methods=["get"])
    def tree_view(self, request):
        """目录树视图"""
        show_deleted = request.query_params.get("show_deleted") == "true"
        project_key = request.query_params.get(
            "project_key", DEFAULT_PROJECT_PROJECT_KEY
        )

        tree_data = PageModelHandler().tree_data(
            show_deleted=show_deleted,
            project_key=project_key,
        )
        return Response(tree_data)

    @swagger_auto_schema(
        operation_summary="获取单个页面简要",
    )
    @action(detail=True, methods=["get"])
    def children(self, request, *args, **kwargs):
        """下一级子目录"""
        obj = self.get_object()
        children = PageShortcutSerializer(obj.get_children(), many=True)
        return Response(children.data)

    @swagger_auto_schema(
        operation_summary="页面迁移",
        query_serializer=PageMoveSerializer(),
    )
    @action(detail=True, methods=["put"])
    def move(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = PageMoveSerializer(data=request.data, instance=instance)
        serializer.is_valid(raise_exception=True)
        serializer.update(instance, serializer.validated_data)
        return Response()

    @swagger_auto_schema(
        operation_summary="页面用户展示设置",
        query_serializer=PageDisplayByRole(),
    )
    @action(detail=True, methods=["post"])
    def change_display(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
        serializer = PageDisplayByRole(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.update(instance, serializer.validated_data)
        return Response(serializer.data)

    @swagger_auto_schema(operation_summary="获取项目下所有列表页面")
    @action(detail=False, methods=["get"])
    def get_list_in_project(self, request, *args, **kwargs):
        project_key = request.query_params.get("project_key")
        if not project_key:
            return Response()
        list_page_in_project = PageComponentHandler.get_page_config_in_project(
            project_key=project_key, page_type="LIST"
        )
        return Response(data=list_page_in_project)


class PageComponentViewSet(ModelViewSet):
    queryset = PageComponent.objects.all()
    serializer_class = PageComponentSerializer
    permission_classes = (PageComponentPermission,)

    @swagger_auto_schema(
        operation_summary="页面组件展示",
        query_serializer=PageComponentListSerializer(),
    )
    def list(self, request, *args, **kwargs):
        page_id = request.query_params.get("page_id")
        if not page_id:
            return Response()
        serializer = PageComponentListSerializer(data={"page_id": page_id})
        serializer.is_valid(raise_exception=True)

        page = Page.objects.get(id=page_id)
        component_list = page.component_list
        if component_list:
            ordering = "FIELD(`id`, {})".format(
                ",".join(["'{}'".format(v) for v in component_list])
            )
            self.queryset = self.queryset.filter(
                page_id=serializer.validated_data["page_id"]
            ).extra(select={"ordering": ordering}, order_by=["ordering"])
        else:
            self.queryset = self.queryset.filter(
                page_id=serializer.validated_data["page_id"]
            )
        return super(PageComponentViewSet, self).list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="页面组件创建",
        query_serializer=PageComponentSerializer(),
    )
    def create(self, request, *args, **kwargs):
        return super(PageComponentViewSet, self).create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="页面内组件批量更新(更新，删除，新建)",
        request_body=BatchComponentsSerializer(),
    )
    @action(detail=False, methods=["post"])
    def batch_save(self, request, *args, **kwargs):
        serializer = BatchComponentsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        components = serializer.validated_data["components"]
        page_id = serializer.validated_data["page_id"]
        queryset = PageComponentHandler().batch_save(
            components=components, page_id=page_id
        )
        return Response(PageComponentSerializer(queryset, many=True).data)

    @swagger_auto_schema(
        operation_summary="页面内组件动作",
    )
    @action(detail=False, methods=["get"])
    def get_components_action(self, request, *args, **kwargs):
        project_key = request.query_params.get("project_key")
        if not project_key:
            return Response()
        pages = PageModelHandler().filter(
            ~Q(key="root"),
            ~Q(type__in=["GROUP", "CHART"]),
            project_key=project_key,
            is_deleted=False,
        )
        all_actions_in_page = []
        for item in pages:
            data_struct = dict()
            data_struct["page_id"] = item.id
            data_struct["page_name"] = item.name
            data_struct["page_type"] = item.type
            data_struct.setdefault("actions", [])
            actions = PageComponentHandler().get_page_components_actions(page_obj=item)
            data_struct["actions"].extend(actions)

            all_actions_in_page.append(data_struct)
        return Response(data=all_actions_in_page)

    @swagger_auto_schema(
        operation_summary="设置列表组件展示模式",
    )
    @action(detail=False, methods=["post"])
    def batch_update_list_show_mode(self, request):
        serializer = SetShowModeListSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        components = serializer.validated_data["components"]
        for item in components:
            show_mode_dict = {}
            show_mode_dict.setdefault("mode", item["show_mode"])
            show_mode_dict.setdefault("display_type", PERSON)
            show_mode_dict.setdefault("display_role", item["display_role"])

            list_component = PageComponentHandler(component_id=item["component_id"])
            list_component.update_show_mode(show_mode_dict)
        return Response()

    @swagger_auto_schema(
        operation_summary="生成一个页面访问链接",
        request_body=GenerateOpenLinkSerializer(),
    )
    @action(detail=False, methods=["post"])
    def generate_open_link(self, request):
        serializer = GenerateOpenLinkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        url = PageOpenLinkHandler(data=data).generate_link()
        return Response({"url": url})

    @swagger_auto_schema(
        operation_summary="删除一个页面的表单外链配置", request_body=ClearOpenLinkSerializer()
    )
    @action(detail=False, methods=["post"])
    def clear_open_link(self, request):
        serializer = ClearOpenLinkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        PageOpenLinkHandler(data=None).clear_old_links(page_id=data["page_id"])
        return Response()


class PageComponentCollectionViewSet(NormalModelViewSet):
    queryset = PageComponentCollection.objects.all()
    serializer_class = PageComponentCollectionSerializer

    @action(detail=False, methods=["GET"])
    def get_user_collection(self, request, *args, **kwargs):
        data = PageComponentCollectionHandler().get_user_collection_component(
            request.user.username
        )
        return Response(data)

    @swagger_auto_schema(
        query_serializer=PageComponentCollectionSerializer(),
    )
    @action(detail=False, methods=["delete"])
    def cancel_collection(self, request, *args, **kwargs):
        user = request.user
        component_id = request.query_params.get("component_id")
        instance = self.queryset.get(component_id=component_id, username=user.username)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        operation_summary="获取用户收藏的功能卡片",
    )
    @action(detail=False, methods=["get"])
    def collection_of_page(self, request, *args, **kwargs):
        page_id = request.query_params.get("page_id")
        # component_ids = request.query_params.get("component_ids")
        if not page_id:
            return Response()
        if PageHandler().get_page_type(page_id) != "FUNCTION":
            return Response("该页面不是功能页面")

        collection_set = set(
            PageComponentCollectionHandler().get_user_page_all_collection(
                user=request.user, page_id=page_id
            )
        )

        return Response(
            data={
                "page_id": page_id,
                "collection_components": list(collection_set),
            }
        )
