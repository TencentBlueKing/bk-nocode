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
import datetime
import json
import uuid

from django.conf import settings
from django.db import transaction

from nocode.base.base_handler import APIModel
from nocode.base.basic import get_random_key
from nocode.base.constants import (
    DEFAULT_PROJECT_PROJECT_KEY,
    DEFAULT_ORDER,
    ROOT_ORDER,
    OPEN,
    FUNCTION_CARD,
    LINK_CARD,
)
from nocode.page.handlers.moudle_handler import ProjectHandler, ProjectVersionHandler
from nocode.page.handlers.role_handler import RoleHandler
from nocode.page.models import (
    Page,
    PageComponent,
    PageComponentCollection,
    PageOpenRecord,
)
from django.utils.translation import ugettext as _


class PageModelHandler(APIModel):
    def __init__(self, page_id=None, instance=None, **kwargs):
        self.page_id = page_id
        self.obj = instance
        self.kwarg = kwargs
        super(PageModelHandler, self).__init__()

    def _get_instance(self):
        try:
            if self.page_id is None:
                obj = Page.objects.get(**self.kwarg)
            else:
                obj = Page.objects.get(pk=self.page_id)
            return obj
        except Page.DoesNotExist:
            return None

    @property
    def instance(self):
        if self.obj is None:
            self.obj = self._get_instance()
        return self.obj

    @property
    def all_page(self):
        return Page.objects.all().order_by("order")

    @property
    def exist(self):
        return True if self.instance else False

    def filter(self, *args, **kwargs):
        return self.all_page.filter(*args, **kwargs)

    def get_children(self, **kwargs):
        children = self.instance.get_children().order_by("order")
        if not kwargs:
            return children
        return children.filter(**kwargs)

    def create_root(self, **kwargs):
        return self.create_page(
            key="root", name=_("根目录"), order=ROOT_ORDER, is_deleted=False, **kwargs
        )

    @transaction.atomic
    def create_page(self, name, key=None, parent=None, is_deleted=False, **kwargs):
        if parent is None and kwargs.get("parent_key"):
            parent = Page.objects.get(key=kwargs.get("parent_key"))

        project_key = kwargs.get("project_key", DEFAULT_PROJECT_PROJECT_KEY)
        order = kwargs.get("order", DEFAULT_ORDER)
        if key is None:
            key = get_random_key(name)

        new_page = Page._objects.get_or_create(
            defaults={
                "name": name,
                "parent": parent,
            },
            **{
                "key": key,
                "is_deleted": is_deleted,
                "project_key": project_key,
                "order": order,
            }
        )
        return new_page

    def tree_data(self, show_deleted=False, project_key=DEFAULT_PROJECT_PROJECT_KEY):
        roots = self.filter(level=0, is_deleted=False, project_key=project_key)

        roots = roots.order_by("id")

        tree = [self.subtree(root, show_deleted=show_deleted) for root in roots]

        return tree

    def filter_permit_tree(self, username, node):
        """获取以node为根的子树"""

        # 根据catalogs列表,用户角色筛选
        node_children = node["children"]

        # 过滤用户有权限的 node_children
        permit_node_children = []
        for child in node_children:
            if child["display_type"] == OPEN:
                permit_node_children.append(child)
                continue
            users = RoleHandler.get_users_by_type(
                child["display_type"], child["display_role"]
            )
            if username in users:
                permit_node_children.append(child)

        # 递归查询，sql查询次数过多
        children = [
            self.filter_permit_tree(username, child) for child in permit_node_children
        ]

        data = {
            "id": node["id"],
            "key": node["key"],
            "type": node["type"],
            "name": "{} (已删除)".format(node["name"])
            if node["is_deleted"]
            else node["name"],
            "is_deleted": node["is_deleted"],
            "desc": node["desc"],
            "parent_id": node["parent_id"],
            "parent_name": node["parent_name"],
            "children": children,
            "order": node["order"],
            "project_key": node["project_key"],
            "display_type": node["display_type"],
            "display_role": node["display_role"],
            "icon": node["icon"],
            "component_list": node["component_list"],
        }

        return data

    def subtree(self, node, show_deleted=False):
        """获取以node为根的子树"""

        # 根据catalogs列表,用户角色筛选
        node_children = node.get_children()
        # 展示删掉的目录
        if not show_deleted:
            node_children = node_children.filter(is_deleted=False).order_by("order")

        # 递归查询，sql查询次数过多
        children = [
            self.subtree(child, show_deleted=show_deleted) for child in node_children
        ]

        data = {
            "id": node.id,
            "key": node.key,
            "type": node.type,
            "name": _("{} (已删除)").format(node.name) if node.is_deleted else node.name,
            "is_deleted": node.is_deleted,
            # "level": node.level,
            "desc": node.desc,
            "parent_id": getattr(node.parent, "id", ""),
            "parent_name": getattr(node.parent, "name", ""),
            # 默认展开一级
            # "expanded": node.level == 0,
            "children": children,
            "order": node.order,
            # "route": node.route,
            "project_key": node.project_key,
            "display_type": node.display_type,
            "display_role": node.display_role,
            # 配合前端，设置图标
            # "openedIcon": "icon-folder-open",
            # "closedIcon": "icon-folder",
            "icon": node.icon,
            "component_list": node.component_list,
        }

        return data


class PageComponentHandler(APIModel):
    def __init__(self, component_id=None, instance=None, **kwargs):
        self.component_id = component_id
        self.obj = instance
        self.kwarg = kwargs
        self.current_components_in_page = []
        super(PageComponentHandler, self).__init__()

    def _get_instance(self):
        try:
            if self.component_id is None:
                obj = PageComponent.objects.get(**self.kwarg)
            else:
                obj = PageComponent.objects.get(pk=self.component_id)
            return obj
        except PageComponent.DoesNotExist:
            return None

    @property
    def instance(self):
        if self.obj is None:
            self.obj = self._get_instance()
        return self.obj

    @property
    def exist(self):
        return True if self.instance else False

    @property
    def all_component(self):
        return PageComponent.objects.all()

    def filter(self, *args, **kwargs):
        return self.all_component.filter(*args, **kwargs)

    def get_page_related_component(self, page_id):
        return self.all_component.filter(page_id=page_id)

    def batch_save(self, components, page_id):
        current_ids = []

        with transaction.atomic():
            for item in components:

                if item.get("id") is not None:
                    current_ids.append(item["id"])
                    self.update_data(item)
                else:
                    instance = self.save_data(item)
                    current_ids.append(instance.id)

            all_ids = set(self.filter(page_id=page_id).values_list("id", flat=True))
            remove_ids = all_ids - set(self.current_components_in_page)
            page = PageModelHandler(page_id=page_id).instance
            page.component_list = current_ids
            page.save()
            self.delete(remove_ids)
        return self.filter(page_id=page_id, id__in=current_ids)

    def uniqid(self):
        return uuid.uuid3(uuid.uuid1(), uuid.uuid4().hex).hex

    def restore_card_by_type(self, item, page_id, group_type):
        from nocode.page.serializers.serializers import PageComponentSerializer

        if group_type == "FUNCTION_GROUP":
            card_struct_data = FUNCTION_CARD
        else:
            card_struct_data = LINK_CARD

        card_struct_data["page_id"] = page_id
        card_struct_data.update(item)
        serializer = PageComponentSerializer(data=card_struct_data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    def update_list_component(self, item):
        for button_group in item["config"]["buttonGroup"]:
            if "id" not in button_group:
                button_group["id"] = self.uniqid()

        for option in item["config"]["optionList"]:
            if "id" not in option:
                option["id"] = self.uniqid()

    def save_card_in_group(self, item):
        children = item.pop("children")
        component_list = []
        for child in children:
            card_data = self.restore_card_by_type(child, item["page_id"], item["type"])
            instance = PageComponent.objects.create(**card_data)
            component_list.append(instance.id)
        item["config"]["component_order"] = component_list
        self.current_components_in_page += component_list

    def update_card_in_group(self, item):
        new_cards = item.pop("children")
        card_group = PageComponent.objects.get(id=item["id"])
        # 更新，新增内部卡片
        new_card_list = []
        for card in new_cards:
            if "id" in card:
                # 更新
                instance = PageComponent.objects.get(id=card["id"])
                for key, value in card.items():
                    if hasattr(instance, key):
                        setattr(instance, key, value)
                    instance.save()
                    new_card_list.append(instance.id)
                continue
            # 新增
            card_data = self.restore_card_by_type(card, item["page_id"], item["type"])
            instance = PageComponent.objects.create(**card_data)

            new_card_list.append(instance.id)

        card_group.config["meta"]["component_order"] = new_card_list
        self.current_components_in_page += new_card_list
        card_group.save()

    def update_data(self, item):
        instance = PageComponent.objects.get(id=item["id"])
        item.setdefault("update_at", datetime.datetime.now())
        if item["type"] == "LIST":
            self.update_list_component(item)
        if item["type"] == ["FUNCTION_GROUP", "LINK_GROUP"]:
            self.update_card_in_group(item)
        if item["type"] == "TAB":
            children_component = item.pop("children", [])
            new_component_order = []
            if children_component:
                for component in children_component:
                    if "id" not in component:
                        new_component = self.save_data(component)
                        new_component_order.append(new_component.id)
                        continue
                    update_component = self.update_data(component)
                    new_component_order.append(update_component.id)

            item["config"]["component_order"] = new_component_order
            self.current_components_in_page += new_component_order

        for key, value in item.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        instance.save()
        self.current_components_in_page.append(instance.id)
        return instance

    def save_data(self, item):
        from nocode.page.serializers.serializers import PageComponentSerializer

        # 按钮分配id
        if item["type"] == "LIST":
            self.update_list_component(item)
        if item["type"] in ["FUNCTION_GROUP", "LINK_GROUP"]:
            self.save_card_in_group(item)
        if item["type"] == "TAB":
            children_component = item.pop("children", [])
            children_ids_list = []
            if children_component:
                for item in children_component:
                    serializer = PageComponentSerializer(data=item)
                    serializer.is_valid(raise_exception=True)
                    instance = self.save_data(serializer.validated_data)
                    children_ids_list.append(instance.id)
            item["config"]["component_order"] = children_ids_list
        instance = PageComponent.objects.create(**item)
        self.current_components_in_page.append(instance.id)
        return instance

    def delete(self, remove_ids):
        PageComponent.objects.filter(id__in=remove_ids).delete()

    def get_page_components_actions(self, page_obj):
        """
        data_struct: {
            "id": page_id,
            "name": page_name,
            "action": [
                {
                    "id": component_id/button_id
                    "name": component_name/button_name/提交(page_type=SHEET)
                }
            ]
        }
        """
        page_components = self.filter(page_id=page_obj.id)
        page_type = page_obj.type

        actions = []
        if not page_components:
            return actions

        if page_type == "FUNCTION":
            for item in page_components:
                component_info = dict()
                component_info.setdefault("id", item.id)
                component_info.setdefault("name", item.config["name"])
                actions.append(component_info)

        if page_type == "SHEET":
            component_info = dict()
            component = page_components.first()
            component_info.setdefault("id", component.id)
            component_info.setdefault("name", "提交")
            actions.append(component_info)

        if page_type == "LIST":
            """
             "buttonGroup": [
                {"option": "HEADER",
                "value": 9,
                "name": "add",
                "type": "ADD",
                "id": "cea6cbe670743635bb255008a8db0b26"
                }
            ]
            """
            component = page_components.first()

            for button in component.config["buttonGroup"]:
                component_info = dict()
                component_info.setdefault("id", button["id"])
                component_info.setdefault("name", button["name"])
                actions.append(component_info)

            for button in component.config["optionList"]:
                """
                "optionList":[
                    {
                        "option": "INNER",
                        "value": "",
                        "name": "默认",
                        "type": "",
                        "id": "8e12462cd6c234ac83cf586d0e36ca89"
                    }
                ]
                """
                component_info = dict()
                component_info.setdefault("id", button["id"])
                component_info.setdefault("name", button["name"])
                actions.append(component_info)

        if page_type == "CUSTOM":
            page_components = page_components.filter(type__in=["FUNCTION", "LINK"])
            for item in page_components:
                component_info = dict()
                component_info.setdefault("id", item.id)
                component_info.setdefault("name", item.config["name"])
                actions.append(component_info)

        return actions

    @classmethod
    def get_page_config_in_project(cls, project_key, page_type=None):
        pages = (
            PageModelHandler()
            .filter(project_key=project_key, type=page_type)
            .values("id", "name")
        )
        res_data = []
        for page in pages:
            page_data = dict()
            page_data["id"] = page.get("id")
            page_data["name"] = page.get("name")

            page_data.setdefault("components", [])
            page_components = (
                cls().filter(page_id=page.get("id")).values("id", "config")
            )
            for component in page_components:
                page_data["components"].append(component)
            res_data.append(page_data)
        return res_data

    def update_show_mode(self, show_mode_data):
        self.instance.config["show_mode"] = show_mode_data
        self.instance.save()


class PageComponentCollectionHandler:
    def __init__(self):
        self.component_page_dict = {}
        self.project_component_ids = {}

    def get_components(self, project_key, page_components):
        data = []
        computed_page_ids = set()
        component_ids = self.project_component_ids[project_key]
        for component_id in component_ids:
            page_id = self.component_page_dict.get(component_id)
            if page_id not in page_components:
                continue
            if page_id in computed_page_ids:
                continue
            components = page_components[page_id]
            computed_page_ids.add(page_id)
            for items in components:
                if items["id"] in component_ids:
                    if isinstance(items["config"], str):
                        items["config"] = json.loads(items["config"])
                    data.append(items)
        return data

    def get_user_collection_component(self, username):
        collections = PageComponentCollection.objects.filter(username=username).values(
            "project_key", "component_id", "page_id"
        )

        data = {}

        project_keys = set([collection["project_key"] for collection in collections])
        for collection in collections:
            self.project_component_ids.setdefault(collection["project_key"], []).append(
                collection["component_id"]
            )

        self.component_page_dict = {
            collection["component_id"]: str(collection["page_id"])
            for collection in collections
        }

        projects = ProjectHandler().get_projects_versions(project_keys=project_keys)

        for project in projects:
            current_project_version = ProjectVersionHandler(
                project.key, project.version_number
            )
            components = current_project_version.get_version_page_components()
            page_components = self.get_components(project.key, components)
            if len(page_components) > 0:
                data[project.key] = {
                    "project_name": project.name,
                    "project_logo": project.logo,
                    "project_color": json.loads(project.color),
                    "project_version": project.version_number,
                    "project_config": current_project_version.get_version_project_config(),
                    "components": page_components,
                }
        return data

    def get_user_page_all_collection(self, user, page_id):
        return PageComponentCollection.objects.filter(
            username=user.username, page_id=page_id
        ).values_list("component_id", flat=True)


class PageOpenLinkHandler:
    def __init__(self, data):
        self.data = data

    def generate_token(self):
        return uuid.uuid3(uuid.uuid1(), uuid.uuid4().hex).hex

    def clear_old_links(self, page_id):
        PageOpenRecord.objects.filter(page_id=page_id).delete()

    def generate_link(self):
        page_id = self.data.get("page_id")

        # 清理旧的数据
        self.clear_old_links(page_id=page_id)

        end_time = self.data.get("end_time")
        project_key = self.data.get("project_key")
        service_id = self.data.get("service_id")

        token = self.generate_token()
        # 创建一条新的纪录
        PageOpenRecord.objects.create(
            page_id=page_id,
            end_time=end_time,
            token=token,
            service_id=service_id,
            project_key=project_key,
        )
        url = "{}form/{}".format(settings.FRONTEND_URL, token)
        return url

    @classmethod
    def open_record_exist(cls, page_id, service_id):
        now = datetime.datetime.now()
        return PageOpenRecord.objects.filter(
            page_id=page_id, service_id=service_id, end_time__gte=now
        ).exists()
