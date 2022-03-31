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

from rest_framework import serializers
from rest_framework.fields import JSONField
from django.utils.translation import ugettext as _
from bulk_update.helper import bulk_update

from itsm.project.handler.project_handler import ProjectHandler
from itsm.project.models import Project
from nocode.base.constants import (
    ROOT_ORDER,
    DISPLAY_CHOICES,
    LEN_LONG,
    OPEN,
    EMPTY_STRING,
    FIRST_ORDER,
    MANAGER,
    ONLY_MANAGER,
)
from nocode.page.handlers.moudle_handler import ProjectVersionHandler
from nocode.page.handlers.role_handler import RoleHandler
from nocode.page.models import Page, PageComponent, PageComponentCollection
from nocode.page.handlers.page_handler import PageModelHandler, PageComponentHandler
from nocode.project_manager.handlers.operate_handler import OperateLogHandler


class PageSerializer(serializers.ModelSerializer):
    key = serializers.CharField(required=False, help_text="页面唯一标识")
    project_key = serializers.CharField(required=True, help_text="项目标识")
    name = serializers.CharField(required=True, help_text="页面名称")
    type = serializers.CharField(required=True, help_text="页面类型")

    def validate_project_key(self, value):
        try:
            # 获取应用
            ProjectHandler(project_key=value).instance
        except (Project.DoesNotExist, ValueError):
            raise serializers.ValidationError("该应用不存在")
        return value

    def validate(self, attrs):
        name = attrs.get("name")
        # 父级页面校验
        parent = attrs.get("parent")
        parent_handler = PageModelHandler(instance=parent)
        # 禁止根页面创建
        if not parent:
            parent = parent_handler.filter(
                key="root",
                name=_("根目录"),
                is_deleted=False,
                order=ROOT_ORDER,
                project_key=attrs.get("project_key"),
            ).first()
            attrs["parent"] = parent
            parent_handler = PageModelHandler(instance=parent)

        # 同等级目录下不能同名, order设置排序
        if self.context["view"].action == "create":
            if parent and parent_handler.get_children(
                name=name,
                is_deleted=False,
            ):
                raise serializers.ValidationError(detail=_("同级下页面名称不能重复，请修改后提交"))
            # 设置排序
            children = parent.get_children()
            if children:
                attrs["order"] = len(children) + 1

        if self.context["view"].action == "update":
            if (
                parent
                and parent_handler.get_children(name=name, is_deleted=False)
                .exclude(id=self.instance.id)
                .exists()
            ):
                raise serializers.ValidationError(detail=_("同级下页面名称不能重复，请修改后提交"))
            attrs.pop("parent")
        return attrs

    def to_representation(self, instance):
        data = super(PageSerializer, self).to_representation(instance=instance)
        data["children"] = [
            {
                "id": node.id,
                "key": node.key,
                "type": node.type,
                "name": node.name,
                "is_deleted": node.is_deleted,
                "desc": node.desc,
                "parent_id": getattr(node.parent, "id", ""),
                "parent_name": getattr(node.parent, "name", ""),
                "order": node.order,
                "project_key": node.project_key,
                "display_type": node.display_type,
                "display_role": node.display_role,
                "icon": node.icon,
                "component_list": node.component_list,
            }
            for node in instance.get_children()
        ]
        return data

    class Meta:
        model = Page
        fields = "__all__"


class PageShortcutSerializer(serializers.ModelSerializer):
    """服务目录简化序列化"""

    parent_id = serializers.CharField(
        required=False, allow_blank=True, source="parent.id"
    )
    parent_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Page
        fields = (
            "id",
            "name",
            "parent_id",
            "parent_name",
            "display_type",
            "display_role",
        )


class PageDisplayByRole(serializers.ModelSerializer):
    """页面展示范围"""

    name = serializers.CharField(required=False)
    project_key = serializers.CharField(required=True, help_text=_("项目关键字"))
    # 可见范围
    display_type = serializers.ChoiceField(
        required=True, choices=DISPLAY_CHOICES, help_text="可见范围"
    )
    display_role = serializers.CharField(
        required=False, max_length=LEN_LONG, help_text="用户组"
    )
    manager = serializers.IntegerField(
        required=False,
        write_only=True,
        help_text="仅该项目管理组可见：设置为1 display_type=GENERAL  /0",
    )

    def validate(self, attrs):
        project_key = attrs.get("project_key")
        try:
            # 获取应用
            ProjectHandler(project_key=project_key).instance
        except (Project.DoesNotExist, ValueError):
            raise serializers.ValidationError(_("该应用不存在"))
        if attrs.get("manager"):
            try:
                if attrs["manager"] == ONLY_MANAGER:
                    # 设置为仅管理员可见, 角色组表中获取该应用管理组
                    manager_group = RoleHandler.get_group(
                        display_type=attrs["display_type"],
                        role_key=MANAGER,
                        project_key=project_key,
                    )
                    attrs["display_role"] = manager_group.id
                    attrs["display_name"] = manager_group.role_key
                    return attrs
            except Exception as e:
                raise serializers.ValidationError(_(f"修改用户展示错误：{e}"))
        else:
            if attrs["display_type"] == OPEN:
                attrs["display_role"] = EMPTY_STRING
                attrs["display_name"] = EMPTY_STRING
            else:
                if "display_role" not in attrs:
                    raise serializers.ValidationError(_("display_role 为必填项"))
        return attrs

    def update(self, instance, validated_data):
        project = ProjectHandler(
            project_key=validated_data.get("project_key")
        ).instance.name

        display_name = validated_data.pop("display_name")
        if validated_data["display_type"] == OPEN:
            OperateLogHandler.log_create(
                content="{username}可见{project}应用范围更改: {display_type}:{display_name}".format(
                    project=project,
                    username=self.context["request"].user.username,
                    display_type=validated_data.get("display_type"),
                    display_name=display_name,
                ),
                operator=self.context["request"].user.username,
                project_key=instance.project_key,
                module=instance.name,
            )
        else:
            OperateLogHandler.log_create(
                content="{username}可见范围更改，仅{project}管理员可见: {display_type}:{display_name}".format(
                    project=project,
                    username=self.context["request"].user.username,
                    display_type=validated_data.get("display_type"),
                    display_name=display_name,
                ),
                operator=self.context["request"].user.username,
                project_key=instance.project_key,
                module=instance.name,
            )

        return super(PageDisplayByRole, self).update(instance, validated_data)

    class Meta:
        model = Page
        fields = (
            "id",
            "name",
            "project_key",
            "parent_id",
            "display_type",
            "display_role",
            "manager",
        )


class PageMoveSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    type = serializers.CharField(required=False)
    parent_id = serializers.CharField(
        required=False, write_only=True, help_text="新层级父页面"
    )
    project_key = serializers.CharField(required=True, help_text="项目关键字")
    new_order = serializers.IntegerField(
        required=True, write_only=True, help_text="子页面重排序"
    )

    def validate(self, attrs):
        parent_id = attrs.get("parent_id", None)
        project_key = attrs.get("project_key")

        # 父页面校验
        parent_handler = PageModelHandler(page_id=parent_id)
        if not parent_handler.instance:
            raise serializers.ValidationError(_("该父页面不存在"))
        parent_instance = parent_handler.instance
        if parent_instance.project_key != project_key:
            raise serializers.ValidationError(_("该应用不存在该父页面"))

        # 跨层级
        if int(parent_id) != self.instance.parent.id:
            children = parent_handler.get_children()
            attrs["order"] = len(children) + 1
            attrs["parent"] = parent_instance
            return attrs
        # 非跨层级
        attrs["parent"] = parent_instance
        return attrs

    def update(self, instance, validated_data):
        # 跨层级 子页面修正
        if validated_data.get("order"):
            instance.order = validated_data["order"]
            instance.parent = validated_data["parent"]
            instance.save()
            if instance.order == validated_data.get("new_order"):
                return instance
        # 重排序
        new_order = validated_data.get("new_order")

        # 查询处order>= new_order 的子页面
        order_children = (
            PageModelHandler().filter(parent_id=instance.parent.id).order_by("order")
        )

        order_children_list = list(order_children.values_list("id", flat=True))
        new_list = order_children_list
        # 构建新的排序
        new_list.remove(instance.id)
        new_list.insert(new_order, instance.id)

        ordering = "FIELD(`id`, {})".format(
            ",".join(["'{}'".format(v) for v in new_list])
        )

        pages = (
            PageModelHandler()
            .filter(parent=instance.parent)
            .extra(select={"order": ordering}, order_by=["order"])
        )
        for order, obj in enumerate(pages):
            obj.order = FIRST_ORDER + order
        bulk_update(pages, update_fields=["order"])

        return instance

    class Meta:
        model = Page
        fields = (
            "id",
            "name",
            "type",
            "project_key",
            "parent_id",
            "display_type",
            "display_role",
            "new_order",
        )


class PageComponentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    page_id = serializers.IntegerField(required=True, help_text="页面id")
    type = serializers.CharField(required=True, help_text="页面组件类型")
    config = JSONField(required=False, initial={}, help_text="页面组件配置")
    value = serializers.CharField(required=False, help_text="组件绑定值", allow_blank=True)
    children = serializers.JSONField(required=False, help_text="容器类型组件下的组件")

    def validate(self, attrs):
        page_id = attrs.get("page_id")
        page = PageModelHandler(page_id=page_id)
        if not page.exist:
            raise serializers.ValidationError(detail=_("没有该页面"))
        if page.instance.type == "GROUP":
            raise serializers.ValidationError(detail=_("页面组件不允许绑定在组页面下"))

        component_type = attrs.get("type")
        if page.instance.type != "CUSTOM" and component_type != page.instance.type:
            raise serializers.ValidationError(detail=_("非自定义页面,只能绑定在同类型页面下"))

        if component_type in ["FUNCTION", "LINK"]:
            if not attrs["config"].get("name"):
                raise serializers.ValidationError(_("卡片名称不可为空"))
            if not attrs.get("value"):
                raise serializers.ValidationError(_("卡片值不可为空"))

        if attrs["type"] == "TAB":
            if "children" not in attrs:
                raise serializers.ValidationError(
                    detail=_("当为选项卡组件的时候后，children参数时必须的")
                )
            if attrs["children"]:
                [self.run_validation(item) for item in attrs["children"]]

        return attrs

    def to_representation(self, instance):
        data = super(PageComponentSerializer, self).to_representation(instance)
        data.setdefault("children", [])
        if data["config"].get("component_order"):
            component_queryset = PageComponent.objects.filter(
                id__in=data["config"]["component_order"]
            )
            for item in component_queryset:
                data["children"].append(self.to_representation(item))
        return data

    class Meta:
        model = PageComponent
        fields = "__all__"


class PageComponentListSerializer(serializers.Serializer):
    page_id = serializers.CharField(required=True)

    def validate_page_id(self, value):
        if not PageModelHandler(page_id=value).exist:
            raise serializers.ValidationError(detail=_("对应的页面不存在！"))
        return value


class PageListSerializer(serializers.Serializer):
    project_key = serializers.CharField(required=True)

    def validate_project_key(self, value):
        if not ProjectHandler(project_key=value).exist:
            raise serializers.ValidationError(detail=_("对应的项目不存在！"))
        return value


class BatchComponentsSerializer(serializers.Serializer):
    components = serializers.ListField(
        help_text=_("页面批量保存页面组件数据列表"), child=PageComponentSerializer(), min_length=0
    )
    page_id = serializers.IntegerField(help_text=_("页面id"))


class PageComponentCollectionSerializer(serializers.ModelSerializer):
    component_id = serializers.IntegerField(required=True, help_text="页面组件的id")
    page_id = serializers.IntegerField(required=False, help_text="页面组件的id")
    username = serializers.CharField(required=False)
    project_key = serializers.CharField(required=False)

    def validate(self, attrs):

        component_id = attrs.get("component_id")
        username = attrs.get("username")

        if PageComponentCollection.objects.filter(
            component_id=component_id, username=username
        ).exists():
            raise serializers.ValidationError(detail=_("不允许重复收藏！"))

        component = PageComponentHandler(component_id=component_id).instance
        if component is None:
            raise serializers.ValidationError(detail=_("对应的服务组件不存在！"))
        if component.type != "FUNCTION":
            raise serializers.ValidationError(detail=_("只允许收藏功能卡片！"))

        attrs["page_id"] = component.page_id
        attrs["username"] = self.context["request"].user.username
        attrs["project_key"] = Page.objects.get(pk=component.page_id).project_key

        return attrs

    def create(self, validated_data):
        return super(PageComponentCollectionSerializer, self).create(validated_data)

    def to_representation(self, instance):
        data = super(PageComponentCollectionSerializer, self).to_representation(
            instance
        )
        project_key = Page.objects.get(pk=data["page_id"]).project_key
        project = ProjectHandler(project_key=project_key).instance

        current_project_version = ProjectVersionHandler(
            project.key, project.version_number
        )
        data["project_config"] = current_project_version.get_version_project_config()
        return data

    class Meta:
        model = PageComponentCollection
        fields = "__all__"


class ListComponentShowModeSerializer(serializers.Serializer):
    component_id = serializers.CharField(required=True, help_text="列表页面id")
    show_mode = serializers.IntegerField(
        required=True, help_text=" 0:展示所有数据，1:展示用户自己的数据, 2:展示范围选择"
    )
    display_role = serializers.CharField(required=False, default=EMPTY_STRING)

    def validate(self, attrs):
        component_instance = PageComponentHandler(
            component_id=attrs["component_id"]
        ).instance
        if component_instance.type != "LIST":
            raise serializers.ValidationError(_("该页面组件类型不是列表"))

        if attrs["show_mode"] == 2 and not attrs["display_role"]:
            raise serializers.ValidationError(_("请设置展示范围"))
        return attrs


class SetShowModeListSerializer(serializers.Serializer):
    components = serializers.ListField(
        child=ListComponentShowModeSerializer(),
        min_length=0,
        help_text=_("页面批量设置列表数据权限"),
    )


class GenerateOpenLinkSerializer(serializers.Serializer):
    page_id = serializers.IntegerField(help_text=_("页面id"))
    project_key = serializers.CharField(required=True)
    service_id = serializers.IntegerField(help_text=_("功能id"))
    end_time = serializers.DateTimeField(help_text=_("截止日期"))

    def validate_project_key(self, value):
        if not ProjectHandler(project_key=value).exist:
            raise serializers.ValidationError(detail=_("对应的项目不存在！"))
        return value


class ClearOpenLinkSerializer(serializers.Serializer):
    page_id = serializers.IntegerField(help_text=_("页面id"))
    project_key = serializers.CharField(required=True)
