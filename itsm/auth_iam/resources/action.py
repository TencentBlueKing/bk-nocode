# -*- coding: utf-8 -*-

from itsm.auth_iam.resources import ItsmResourceProvider
from nocode.page.models import Page, PageComponent
from nocode.project_manager.models import ProjectVersion
from .basic import ItsmResourceListResult as ListResult
from ...project.models import Project


class ActionResourceProvider(ItsmResourceProvider):
    def get_list_component_data(self, item):
        results = []
        for button_group in item["config"]["buttonGroup"]:
            if "id" not in button_group:
                continue
            results.append(
                {"id": button_group["id"], "display_name": button_group["name"]}
            )

        for option in item["config"]["optionList"]:
            if "id" not in option:
                continue
            results.append({"id": option["id"], "display_name": option["name"]})

        return results

    def list_instance(self, filter, page, **options):
        """
        flow 上层资源为 project
        """

        if not (filter.parent or filter.search or filter.resource_type_chain):
            return ListResult(results=[], count=0)

        if not filter.parent:
            return ListResult(results=[], count=0)

        page_id = filter.parent["id"]
        try:
            page_obj = Page._objects.get(id=page_id)
        except Exception:
            return ListResult(results=[], count=0)

        project = Project.objects.get(key=page_obj.project_key)

        page_component = ProjectVersion.objects.get(
            version_number=project.version_number
        ).page_component

        components = page_component.get(page_id, [])

        data = []
        for component in components:
            if component["type"] == "LIST":
                data.extend(self.get_list_component_data(component))
            if component["type"] == "FUNCTION":
                data.append(
                    {
                        "id": component["id"],
                        "display_name": component["config"].get("name", ""),
                    }
                )
            if component["type"] == "SHEET":
                data.append(
                    {
                        "id": component["id"],
                        "display_name": "提交",
                    }
                )

        count = len(data)
        results = data[page.slice_from : page.slice_to]

        return ListResult(results=results, count=count)

    def get_data(self, page_components):
        data = {}
        for values in page_components.values():
            for item in values:
                if item["type"] == "LIST":
                    continue
                if item["type"] == "SHEET":
                    data[item["id"]] = {"id": str(item["id"]), "display_name": "提交"}
                if item["type"] == "FUNCTION":
                    data[item["id"]] = {
                        "id": str(item["id"]),
                        "display_name": item["config"].get("name", ""),
                    }
        return data

    def fetch_instance_info(self, filter, **options):
        """
        flow 没有定义属性，只处理 filter 中的 ids 字段
        """
        ids = []
        if filter.ids:
            for action_id in filter.ids:
                try:
                    ids.append(int(action_id))
                except Exception:
                    pass
        if not ids:
            return ListResult(results=[])

        page_component_id = ids[0]
        page_component = PageComponent._objects.filter(id=page_component_id).first()
        if page_component is None:
            return ListResult(results=[])

        page_id = page_component.page_id

        page = Page._objects.filter(id=page_id).first()
        if page is None:
            return ListResult(results=[])

        project = Project.objects.get(key=page.project_key)
        page_components = ProjectVersion.objects.get(
            version_number=project.version_number
        ).page_component

        data = self.get_data(page_components)
        results = []
        for item in ids:
            if item in data.keys():
                results.append(data[item])
        return ListResult(results=results)
