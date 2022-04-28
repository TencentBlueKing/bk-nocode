# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.

Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.

BK-ITSM 蓝鲸流程服务 is licensed under the MIT License.

License for BK-ITSM 蓝鲸流程服务:
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

from django.db import transaction
from django.utils.translation import ugettext as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import JSONField
from rest_framework.validators import UniqueValidator
from rest_framework.fields import empty

from itsm.component.constants import (
    DISPLAY_CHOICES,
    EMPTY_LIST,
    EMPTY_STRING,
    LEN_LONG,
    LEN_MIDDLE,
    LEN_NORMAL,
    LEN_XX_LONG,
    SERVICE_CHOICE,
    LEN_SHORT,
    DEFAULT_ENGINE_VERSION,
    NOTIFY_RULE_CHOICES,
    PROCESSOR_CHOICES,
    OPEN,
    SERVICE_SOURCE_CHOICES,
    DEFAULT_PROJECT_PROJECT_KEY,
    PUBLIC_PROJECT_PROJECT_KEY,
    SERVICE_TYPE_CHOICES,
    EMPTY_DICT,
    PERIOD,
    WORKSHEET_RECORD,
    AUTO,
)
from itsm.component.drf.serializers import (
    DynamicFieldsModelSerializer,
    AuthModelSerializer,
)
from itsm.component.exceptions import ServiceCatalogValidateError
from itsm.component.utils.basic import dotted_name, list_by_separator, normal_name
from itsm.component.utils.misc import transform_single_username
from itsm.project.handler.utils import change_so_project_change
from itsm.service.handler.page_handler import PageComponentHandler
from itsm.service.handler.service_handler import ServiceHandler, ServiceCatalogHandler
from itsm.service.handler.worksheet_handler import WorksheetHandler
from itsm.service.models import (
    CatalogService,
    DictData,
    Favorite,
    OldSla,
    Service,
    ServiceCatalog,
    ServiceCategory,
    ServiceSla,
    SysDict,
    FavoriteService,
)
from itsm.service.validators import key_validator, name_validator, time_validator
from itsm.workflow.models import Workflow, Field
from itsm.workflow.serializers import NotifySerializer


class FavoriteSerializer(serializers.ModelSerializer):
    """收藏序列化"""

    name = serializers.CharField(
        required=False, initial=EMPTY_STRING, max_length=LEN_LONG
    )
    service = serializers.CharField(required=True, max_length=LEN_NORMAL)
    data = JSONField(required=True, initial=EMPTY_LIST)

    class Meta:
        model = Favorite
        fields = ("id", "user", "service", "name", "data", "create_at")
        read_only_fields = ("id", "user", "create_at")

    def create(self, validated_data):
        """改写post方法,提供update_or_create逻辑"""

        instance, created = Favorite.objects.update_or_create(
            defaults={"data": validated_data.pop("data")},
            **{
                "user": validated_data.pop("user"),
                "service": validated_data.pop("service"),
            }
        )

        return instance


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ("key", "name", "desc")

    def to_representation(self, instance):
        data = super(ServiceCategorySerializer, self).to_representation(instance)
        data.update({"desc": _(data["desc"])})
        data.update({"name": _(data["name"])})
        return data


class ServiceCatalogSerializer(serializers.ModelSerializer):
    """服务目录序列化"""

    level = serializers.IntegerField(required=False, min_value=0)
    name = serializers.CharField(
        required=True,
        error_messages={"blank": _("名称不能为空")},
        validators=[name_validator],
        max_length=LEN_NORMAL,
    )
    # allow_blank -> 允许字段为空字符串
    desc = serializers.CharField(required=False, max_length=LEN_LONG, allow_blank=True)

    parent__id = serializers.CharField(
        required=False, allow_blank=True, source="parent.id"
    )
    parent__name = serializers.CharField(
        required=False, allow_blank=True, source="parent.name"
    )

    parent_key = serializers.CharField(required=False, allow_blank=True)
    parent_name = serializers.CharField(required=False, allow_blank=True)
    project_key = serializers.CharField(required=True)

    def validate(self, attrs):
        """
        该函数可用于关联字段校验，比如账号密码是否匹配，
        还可以用来自动添加一些read_only字段，比如某些key、转换某些字段等
        """

        from itsm.service.models import ServiceCatalog

        # OrderedDict([(u'parent', {u'id': u'1'}), (u'name', u'\u518d\u6765\u4e00\u904d'), (u'desc', _(u''))])

        parent_object = None

        # 剔除中间字段，若字段不存在，则返回None
        parent_key = attrs.pop("parent_key", None)
        parent = attrs.pop("parent", None)

        # 转换parent_key到parent，parent_id优先级高于parent_key
        if parent_key:
            # TODO 如何更好的获取对应的Model
            try:
                parent_object = ServiceCatalog.objects.get(key=parent_key)
            except (ServiceCatalog.DoesNotExist, ValueError):
                raise ValidationError(_("指定的父目录不存在"))

        if parent:
            try:
                parent_object = ServiceCatalog.objects.get(pk=parent.get("id"))
                # ValueError: invalid literal for int() with base 10: ''
            except (ServiceCatalog.DoesNotExist, ValueError):
                raise ValidationError(_("指定的父目录不存在"))

        # 禁止创建根目录
        if not parent_object and self.context["view"].action == "create":
            raise ServiceCatalogValidateError(_("请提供合法的父级目录"))
        # 限制目录层级为三级
        if parent_object and parent_object.level >= 3:
            raise ServiceCatalogValidateError(_("服务目录最多只支持3级"))

        # 同级下目录名不能重复
        if self.context["view"].action == "create":
            if (
                parent_object
                and parent_object.get_children()
                .filter(is_deleted=False, name=attrs["name"])
                .exists()
            ):
                raise ServiceCatalogValidateError(_("同级下目录名不能重复，请修改后提交"))
        if self.context["view"].action == "update":
            if (
                parent_object
                and parent_object.get_children()
                .filter(is_deleted=False, name=attrs["name"])
                .exclude(id=self.instance.id)
                .exists()
            ):
                raise ServiceCatalogValidateError(_("同级下目录名不能重复，请修改后提交"))

        attrs["parent"] = parent_object

        return attrs

    class Meta:
        model = ServiceCatalog
        fields = (
            "id",
            "key",
            "level",
            "parent",
            "parent_name",
            "parent_key",
            "parent__id",
            "parent__name",
            "name",
            "desc",
            "project_key",
        )
        # 只读字段在创建和更新时均被忽略
        read_only_fields = (
            "id",
            "key",
            "parent_name",
            "parent_key",
            "parent__id",
            "parent__name",
        )


class ServiceCatalogShortcutSerializer(serializers.ModelSerializer):
    """服务目录简化序列化"""

    parent_id = serializers.CharField(
        required=False, allow_blank=True, source="parent.id"
    )
    parent_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = ServiceCatalog
        fields = (
            "id",
            "key",
            "level",
            "name",
            "parent_id",
            "parent_name",
        )


class SlaSerializer(serializers.ModelSerializer):
    """服务级别序列化"""

    name = serializers.CharField(
        required=True,
        error_messages={"blank": _("名称为必填项")},
        max_length=8,
        validators=[
            UniqueValidator(queryset=OldSla.objects.all(), message=_("服务级别名已存在，请重新输入")),
            name_validator,
        ],
    )
    key = serializers.CharField(required=False, max_length=LEN_LONG, allow_blank=True)
    level = serializers.ChoiceField(
        choices=OldSla.level_choices, error_messages={"invalid_choice": _("选项不合法")}
    )
    resp_time = serializers.CharField(
        required=True, error_messages={"blank": _("响应时间为必填项")}
    )
    deal_time = serializers.CharField(
        required=True, error_messages={"blank": _("处理时间为必填项")}
    )
    desc = serializers.CharField(required=False, max_length=LEN_LONG, allow_blank=True)

    class Meta:
        model = OldSla
        fields = (
            "id",
            "key",
            "name",
            "level",
            "resp_time",
            "deal_time",
            "desc",
            "is_builtin",
        )

    def create(self, validated_data):
        validated_data["key"] = OldSla.get_unique_key(validated_data["name"])
        return super(SlaSerializer, self).create(validated_data)

    def validate_resp_time(self, value):
        """resp_time校验"""
        time_validator(value)
        return value

    def validate_deal_time(self, value):
        """deal_time校验"""
        time_validator(value)
        return value

    def to_representation(self, instance):
        data = super(SlaSerializer, self).to_representation(instance)
        data.update({"desc": _(data["desc"])})
        data.update({"name": _(data["name"])})
        return data


class ServiceSlaSerializer(serializers.ModelSerializer):
    """服务与SLA关联表序列化"""

    name = serializers.CharField(
        required=True, error_messages={"blank": _("协议名称不能为空")}, max_length=LEN_LONG
    )
    service_id = serializers.IntegerField(required=False, allow_null=True)
    lines = JSONField(required=False, initial=EMPTY_LIST)
    states = JSONField(required=False, initial=EMPTY_LIST)

    class Meta:
        model = ServiceSla
        fields = "__all__"


class ServiceSerializer(AuthModelSerializer):
    """服务序列化"""

    name = serializers.CharField(
        required=True,
        error_messages={"blank": _("名称不能为空")},
        max_length=LEN_MIDDLE,
        validators=[
            # UniqueValidator(queryset=Service.objects.all(), message=_("服务名已存在，请重新输入")),
            # name_validator
        ],
    )
    key = serializers.CharField(
        required=False,
        error_messages={"blank": _("编码不能为空")},
        max_length=LEN_LONG,
        validators=[key_validator],
    )
    type = serializers.CharField(
        required=True,
        max_length=LEN_LONG,
        validators=[key_validator],
    )
    workflow_name = serializers.CharField(source="workflow.name", required=False)
    workflow = serializers.IntegerField(required=False, source="workflow.id")
    show_all_workflow = serializers.BooleanField(
        required=False, source="workflow.show_all_workflow"
    )
    show_my_create_workflow = serializers.BooleanField(
        required=False, source="workflow.show_my_create_workflow"
    )
    version_number = serializers.CharField(
        source="workflow.version_number", required=False
    )
    desc = serializers.CharField(required=False, max_length=LEN_LONG, allow_blank=True)
    is_valid = serializers.BooleanField(required=False)
    # 默认有默认值
    # display_type = serializers.ChoiceField(required=False, choices=DISPLAY_CHOICES)
    # display_role = serializers.CharField(required=False, max_length=LEN_LONG)
    catalog_id = serializers.IntegerField(required=False)
    project_key = serializers.CharField(required=True, max_length=LEN_SHORT)
    source = serializers.ChoiceField(required=False, choices=SERVICE_SOURCE_CHOICES)
    owners = serializers.CharField(
        required=False, error_messages={"blank": _("服务负责人不能为空")}
    )
    rule_type = serializers.CharField(required=False, default=EMPTY_STRING)
    # TODO sla开始节点结束节点交叉校验
    sla = ServiceSlaSerializer(required=False, many=True)

    # 服务绑定的表单
    worksheet_ids = serializers.ListField(required=True, help_text="用户绑定的表单列表")
    periodic_task = serializers.DictField(
        required=False, help_text="功能周期触发规则", write_only=True
    )
    worksheet_event = serializers.DictField(
        required=False, help_text="表单触发规则", write_only=True
    )

    class Meta:
        model = Service
        fields = (
            "id",
            "key",
            "type",
            "name",
            "desc",
            "workflow",
            "workflow_name",
            "version_number",
            "bounded_catalogs",
            "bounded_relations",
            "catalog_id",
            "is_valid",
            # "display_type",
            # "display_role",
            "owners",
            # "can_ticket_agency",
            "sla",
            "source",
            "project_key",
            "worksheet_ids",
            "show_all_workflow",
            "show_my_create_workflow",
            "rule_type",
            "periodic_task",
            "worksheet_event",
        ) + model.DISPLAY_FIELDS
        read_only_fields = model.DISPLAY_FIELDS

    def __init__(self, instance=None, data=empty, **kwargs):
        super(ServiceSerializer, self).__init__(instance, data, **kwargs)
        self.favorite_service = self.get_favorite_users()

    def get_favorite_users(self):
        services = (
            [self.instance]
            if isinstance(self.instance, Service)
            else []
            if self.instance is None
            else self.instance
        )
        service_ids = [service.id for service in services]
        users = FavoriteService.objects.filter(service_id__in=service_ids).values(
            "service_id", "user"
        )
        service_user_map = {}
        for user in users:
            service_user_map.setdefault(user["service_id"], []).append(user["user"])
        return service_user_map

    def get_catalog_id(self, project_key, operate_type):
        handler = ServiceCatalogHandler(
            project_key=project_key,
            operate_type=operate_type,
        )
        if not handler.exist:
            raise serializers.ValidationError(_("项目操作类型不存在"))
        catalog_id = handler.instance.id
        return catalog_id

    def get_service_related_page(self, service_id):
        page_names = set(PageComponentHandler().get_relate_page(service_id))
        return list(page_names)

    def get_service_related_worksheet(self, worksheet_ids):
        # 根据服务流程获取绑定的表单
        worksheet_items = WorksheetHandler().get_relate_worksheet(worksheet_ids)
        return worksheet_items

    def migrate_field(self, workflow):
        """
        更新和删除类型的流程自动在提单节点生成id字段且不可删除。
        """
        data = {
            "type": "INT",
            "source": "CUSTOM",
            "key": "id",
            "name": "id",
            "is_builtin": True,
            "state_id": workflow.first_state.id,
            "workflow_id": workflow.id,
        }
        field = Field.objects.create(**data).id
        first_state = workflow.first_state
        first_state.fields.append(field)
        first_state.save()

    @transaction.atomic
    def create(self, validated_data):
        """创建后立即绑定"""

        # 同名检测
        service_name = validated_data.get("name")
        if Service.objects.filter(
            name=service_name,
            is_deleted=False,
            project_key=validated_data["project_key"],
        ).exists():
            raise serializers.ValidationError("该应用下已存在名为{}的功能".format(service_name))

        # 初始化一个流程
        work_flow_instance = self.init_work_flow(validated_data)

        if validated_data["type"] in ["EDIT", "DELETE"]:
            self.migrate_field(work_flow_instance)

        # 创建一个新的流程版本
        version = work_flow_instance.create_version()

        # nocode平台默认服务类型key为请求管理
        validated_data["key"] = "request"

        validated_data["workflow"] = version

        if validated_data["type"] == "AUTO":
            # 自动化功能可自我设定是否启用
            validated_data["is_valid"] = validated_data.get("is_valid", False)
        else:
            validated_data["is_valid"] = (
                True if validated_data["type"] in ["DETAIL", "EXPORT"] else False
            )

        validated_data.pop("catalog_id", None)

        catalog_id = self.get_catalog_id(
            project_key=validated_data["project_key"],
            operate_type=validated_data["type"],
        )

        sla_tasks = validated_data.pop("sla", [])

        periodic_task = {}
        worksheet_event = {}
        if validated_data["type"] == AUTO:
            if validated_data["rule_type"] == PERIOD:
                if "periodic_task" not in validated_data:
                    raise serializers.ValidationError("请设置周期运行方案")
                periodic_task = validated_data.pop("periodic_task", {})
            else:
                if "worksheet_event" not in validated_data:
                    raise serializers.ValidationError("请设置表单触发运行方案")
                worksheet_event = validated_data.pop("worksheet_event", {})

        instance = super(ServiceSerializer, self).create(validated_data)

        # 服务根据操作类型绑定到相应的操作目录
        service_handler = ServiceHandler(
            instance=instance, project_key=instance.project_key
        )
        service_handler.bind_operate_catalog(catalog_id)

        # 周期自动化功能
        if instance.type == "AUTO":
            if instance.rule_type == PERIOD:
                # 周期功能触发
                instance.update_periodic_task(periodic_task)
            # 表单记录更新触发
            else:
                instance.update_worksheet_event(worksheet_event)

        # instance.bind_catalog(catalog_id, instance.project_key)
        instance.update_service_sla(sla_tasks)

        change_so_project_change(instance.project_key)

        return instance

    def init_work_flow(self, validated_data):
        work_flow_instance = Workflow.objects.create(
            name="{}_work_flow".format(validated_data["name"]),
            desc="",
            flow_type="other",
            notify_freq="0",
            is_biz_needed=False,
            is_iam_used=False,
            is_enabled=True,
            is_draft=False,
            table_id=1,
            owners="",
            engine_version=DEFAULT_ENGINE_VERSION,
            creator=validated_data["creator"],
            updated_by=validated_data["updated_by"],
        )
        return work_flow_instance

    def update(self, instance, validated_data):
        """更新后重新绑定目录"""

        validated_data.pop("catalog_id", 0)
        # catalog_id = self.get_catalog_id(
        #     project_key=instance.project_key,
        #     type=validated_data["type"]
        # )
        sla_tasks = validated_data.pop("sla", [])
        if instance.key in [DEFAULT_PROJECT_PROJECT_KEY, PUBLIC_PROJECT_PROJECT_KEY]:
            raise serializers.ValidationError(_("禁止对内置服务进行修改"))
        if instance.is_builtin:
            raise serializers.ValidationError(_("禁止对内置服务进行修改"))
        if instance.worksheet_ids != validated_data.get("worksheet_ids"):
            raise serializers.ValidationError(_("禁止对已关联表单进行变更"))

        if instance.type != validated_data["type"]:
            raise serializers.ValidationError(_("禁止变更功能属性"))

        with transaction.atomic():
            # 已经有默认key，key无需更新
            # instance.key = validated_data["key"]
            if (
                "key" in validated_data.keys()
                and validated_data.get("key") != instance.key
            ):
                raise serializers.ValidationError(_("不允许修改服务类型"))
            instance.name = validated_data["name"]
            instance.desc = validated_data["desc"]
            instance.updated_by = validated_data["updated_by"]
            instance.save()
            # instance.bind_catalog(catalog_id, instance.project_key)

            validated_data.pop("catalog_id", None)
            catalog_id = self.get_catalog_id(
                project_key=validated_data["project_key"],
                operate_type=validated_data["type"],
            )
            service_handler = ServiceHandler(
                instance=instance, project_key=instance.project_key
            )
            service_handler.bind_operate_catalog(catalog_id)

            instance.update_service_sla(sla_tasks)

            # 定时自动化专属设置
            if validated_data["type"] == AUTO:
                if instance.rule_type != validated_data["rule_type"]:
                    # 重新初始化
                    if instance.rule_type == PERIOD:
                        instance.update_periodic_task(EMPTY_DICT)
                    else:
                        instance.update_worksheet_event(EMPTY_DICT)

                if validated_data["rule_type"] == PERIOD:
                    if "periodic_task" not in validated_data:
                        raise serializers.ValidationError("请设置周期运行方案")
                    periodic_task = validated_data.pop("periodic_task", {})
                    instance.update_periodic_task(periodic_task)

                else:
                    if "worksheet_event" not in validated_data:
                        raise serializers.ValidationError("请设置表单触发运行方案")
                    worksheet_event = validated_data.pop("worksheet_event", {})
                    instance.update_worksheet_event(worksheet_event)

            super(ServiceSerializer, self).update(instance, validated_data)
            change_so_project_change(instance.project_key)

        return instance

    def to_internal_value(self, data):
        # TODO: 根据未来的校检逻辑可能会有所修改
        data = super(ServiceSerializer, self).to_internal_value(data)
        if "workflow" in data:
            data["workflow"] = data["workflow"]["id"]
        data["display_role"] = dotted_name(data.get("display_role", ""))
        if "owners" in data:
            data["owners"] = dotted_name(data["owners"])

        return data

    def to_representation(self, instance):
        data = super(ServiceSerializer, self).to_representation(instance)

        relate_page = self.get_service_related_page(instance.id)
        relate_worksheet = self.get_service_related_worksheet(instance.worksheet_ids)

        data["relate_page"] = relate_page if relate_page else []
        data["relate_worksheet"] = relate_worksheet
        data["type"] = instance.type
        data["type_name"] = dict(SERVICE_TYPE_CHOICES).get(instance.type)
        workflow_instance = Workflow._objects.get(id=instance.workflow.workflow_id)

        username = self.context["request"].user.username
        data["creator"] = transform_single_username(data["creator"])
        data["updated_by"] = transform_single_username(data["updated_by"])
        data["supervise_type"] = workflow_instance.supervise_type
        data["supervisor"] = workflow_instance.supervisor
        if "display_role" in data:
            data["display_role"] = ",".join(list_by_separator(data["display_role"]))
        data["first_state_id"] = workflow_instance.first_state.id
        data["workflow_id"] = instance.workflow.workflow_id
        data["is_biz_needed"] = workflow_instance.is_biz_needed
        data["notify"] = [
            {"type": notify.type, "name": notify.name}
            for notify in workflow_instance.notify.all()
        ]
        data["notify_rule"] = workflow_instance.notify_rule
        data["notify_freq"] = workflow_instance.notify_freq
        data["is_supervise_needed"] = workflow_instance.is_supervise_needed
        data["revoke_config"] = workflow_instance.revoke_config
        data["extras"] = workflow_instance.extras
        data["owners"] = ",".join(list_by_separator(data["owners"]))
        data["favorite"] = username in self.favorite_service.get(instance.id, [])
        data["period_task"] = (
            instance.get_periodic_task
            if data["type"] == AUTO and data["rule_type"] == PERIOD
            else {}
        )
        data["worksheet_event"] = (
            instance.get_worksheet_event
            if data["type"] == AUTO and data["rule_type"] == WORKSHEET_RECORD
            else {}
        )
        return self.update_auth_actions(instance, data)


class ServiceListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        required=True,
        error_messages={"blank": _("名称不能为空")},
        max_length=LEN_MIDDLE,
        validators=[
            UniqueValidator(queryset=Service.objects.all(), message=_("服务名已存在，请重新输入")),
            # name_validator
        ],
    )
    key = serializers.CharField(
        required=True,
        error_messages={"blank": _("编码不能为空")},
        max_length=LEN_LONG,
        validators=[key_validator],
    )

    def __init__(self, instance=None, data=empty, **kwargs):
        super(ServiceListSerializer, self).__init__(instance, data, **kwargs)
        service_ids = self.get_service_ids()
        self.favorite_service = self.get_favorite_users(service_ids)
        self.service_catalogs_map = self.get_service_catalogs(service_ids)

    def get_service_ids(self):
        """
        一次性获取所有的service.id,方便后面的查询
        return [service.id]
        """
        services = (
            [self.instance]
            if isinstance(self.instance, Service)
            else []
            if self.instance is None
            else self.instance
        )
        return [service["id"] for service in services]

    def get_service_catalogs(self, service_ids):
        """
        获取用户所有部门的catalogs
        """
        service_catalogs_map = {
            cs.service_id: [cs.catalog.name]
            for cs in CatalogService.objects.filter(service_id__in=service_ids)
        }
        return service_catalogs_map

    def get_favorite_users(self, service_ids):
        """
        获取用户最喜欢的服务
        """
        users = FavoriteService.objects.filter(service_id__in=service_ids).values(
            "service_id", "user"
        )
        service_user_map = {}
        for user in users:
            service_user_map.setdefault(user["service_id"], []).append(user["user"])
        return service_user_map

    def to_representation(self, instance):
        data = super(ServiceListSerializer, self).to_representation(instance)
        username = self.context["request"].user.username
        data["favorite"] = username in self.favorite_service.get(instance["id"], [])
        data["bounded_catalogs"] = self.service_catalogs_map.get(instance["id"], [])
        return data

    class Meta:
        model = Service
        fields = ("id", "key", "name", "type")


class CatalogServiceSerializer(serializers.ModelSerializer):
    """服务目录关联序列化"""

    class Meta:
        model = CatalogService
        fields = (
            "id",
            "catalog",
            "service",
        ) + model.DISPLAY_FIELDS
        read_only_fields = model.DISPLAY_FIELDS


class CatalogServiceEditSerializer(serializers.Serializer):
    """服务目录关联操作序列化"""

    catalog_id = serializers.IntegerField(min_value=1, required=True)
    services = serializers.ListField(allow_empty=False, required=True)

    def validate_services(self, value):
        """
        Check services
        """

        if not isinstance(value, list) and len(value) > 0:
            raise serializers.ValidationError(_("请选择至少一项服务"))

        if Service.objects.filter(id__in=value).count() != len(value):
            raise serializers.ValidationError(_("部分服务不存在"))

        return value

    def validate_catalog_id(self, value):
        """
        Check catalog_id
        """

        try:
            catalog = ServiceCatalog.objects.get(id=value)
            if catalog.level == 0:
                raise serializers.ValidationError(_("根目录不允许添加服务，选择其他目录"))
        except ServiceCatalog.DoesNotExist:
            raise serializers.ValidationError(_("指定的服务目录不存在"))

        return value


class DictDataSerializer(serializers.ModelSerializer):
    """数据字典数据项序列化"""

    key = serializers.CharField(
        required=True,
        error_messages={"blank": _("编码不能为空")},
        max_length=LEN_MIDDLE,
        validators=[key_validator],
    )
    name = serializers.CharField(
        required=True,
        error_messages={"blank": _("名称不能为空")},
        max_length=LEN_MIDDLE,
    )
    # validators=[name_validator])
    order = serializers.IntegerField(required=False, min_value=1)

    class Meta:
        model = DictData
        fields = (
            "id",
            "key",
            "name",
            "level",
            "order",
            "parent",
            "parent_key",
            "parent_name",
            "is_readonly",
            "is_builtin",
            "dict_table",
        )
        read_only_fields = (
            "id",
            "level",
            "is_readonly",
            "is_builtin",
            "parent_key",
            "parent_name",
        ) + model.FIELDS


class SysDictSerializer(DynamicFieldsModelSerializer):
    """数据字典序列化"""

    key = serializers.CharField(
        required=True,
        error_messages={"blank": _("编码不能为空")},
        max_length=LEN_MIDDLE,
        validators=[
            UniqueValidator(queryset=SysDict.objects.all(), message=_("编码已存在，请重新输入")),
            key_validator,
        ],
    )
    name = serializers.CharField(
        required=True,
        error_messages={"blank": _("名称不能为空")},
        max_length=LEN_MIDDLE,
    )
    owners = serializers.CharField(
        required=False, max_length=LEN_XX_LONG, allow_blank=True
    )
    desc = serializers.CharField(required=False, max_length=LEN_LONG, allow_blank=True)

    class Meta:
        model = SysDict
        fields = (
            "id",
            "key",
            "name",
            "owners",
            "desc",
            "is_enabled",
            "is_readonly",
        ) + model.DISPLAY_FIELDS

        read_only_fields = model.DISPLAY_FIELDS

    def to_internal_value(self, data):
        data = super(SysDictSerializer, self).to_internal_value(data)
        if "owners" in data:
            data["owners"] = dotted_name(data["owners"])
        return data

    def to_representation(self, instance):
        data = super(SysDictSerializer, self).to_representation(instance)
        data["name"] = _(data["name"])
        data["owners"] = normal_name(data.get("owners"))
        return data


class DictKeySerializer(serializers.Serializer):
    key = serializers.CharField(
        required=True,
        error_messages={"blank": _("编码不能为空")},
        max_length=LEN_MIDDLE,
        validators=[key_validator],
    )
    service = serializers.ChoiceField(required=False, choices=SERVICE_CHOICE)
    view_type = serializers.ChoiceField(
        required=False, choices=["list", "tree", "sets"]
    )


class WorkFlowConfigSerializer(serializers.Serializer):
    is_revocable = serializers.BooleanField(required=True)
    revoke_config = serializers.DictField(required=True)
    notify = NotifySerializer(required=True, allow_null=True, many=True)

    # 流程中显示
    show_all_workflow = serializers.BooleanField(required=True)
    show_my_create_workflow = serializers.BooleanField(required=True)

    notify_freq = serializers.IntegerField(required=False)  # 重试间隔
    notify_rule = serializers.ChoiceField(
        required=False, allow_blank=True, choices=NOTIFY_RULE_CHOICES
    )  # 重试规则
    extras = serializers.JSONField(required=False)
    is_supervise_needed = serializers.BooleanField(required=False)
    supervise_type = serializers.ChoiceField(required=False, choices=PROCESSOR_CHOICES)
    supervisor = serializers.CharField(
        required=False, max_length=LEN_LONG, allow_blank=True
    )


class ServiceConfigSerializer(serializers.Serializer):
    workflow_config = WorkFlowConfigSerializer(required=True)
    # 代办/督办
    can_ticket_agency = serializers.BooleanField(required=False, default=False)
    # 可见范围
    display_type = serializers.ChoiceField(
        required=False, choices=DISPLAY_CHOICES, default=OPEN
    )
    display_role = serializers.CharField(required=False, max_length=LEN_LONG)


class ServiceListQuerySerializer(serializers.Serializer):
    project_key = serializers.CharField(help_text=_("项目key"), required=False)


class ServiceBatchDeleteQuerySerializer(serializers.Serializer):
    id = serializers.CharField(help_text=_("id数组字符串"), required=True)


class ServiceOperateFavQuerySerializer(serializers.Serializer):
    favorite = serializers.BooleanField(
        help_text=_("收藏/取消收藏"), required=False, default=False
    )


class ServiceImportQuerySerializer(serializers.Serializer):
    table_id = serializers.IntegerField(help_text=_("基础模型id"))


class ServiceImportSQuerySerializer(serializers.Serializer):
    service_id = serializers.IntegerField(help_text=_("服务id"))


class ServiceSourceQuerySerializer(serializers.Serializer):
    source = serializers.CharField(help_text=_("来源"))
