# -*- coding: utf-8 -*-
from itsm.component.constants import RECENTLY_USING_LENGTH
from itsm.service.handler.service_handler import ServiceHandler
from itsm.ticket.models import Ticket


class ServiceHandler(ServiceHandler):
    def get_recently_using_service(self, username):
        from itsm.project.handler.project_handler import ProjectHandler

        # 获取全部单据，按照时间排列,并获取关联服务id
        all_service_sorted = (
            Ticket.objects.all()
            .filter(creator=username)
            .order_by("create_at")
            .values_list("service_id", flat=True)
        )
        # 通过set()去重直接获取前4个
        all_service_sorted = set(all_service_sorted)
        recently_using_length = (
            RECENTLY_USING_LENGTH
            if len(all_service_sorted) > RECENTLY_USING_LENGTH
            else len(all_service_sorted)
        )
        all_service_sorted = list(all_service_sorted)[:recently_using_length]
        # 返回服务
        services = self.filter(pk__in=all_service_sorted)

        last_project = dict()
        recent_service = []

        for service in services:

            service_dict = dict()
            service_name = service.name
            service_desc = service.desc
            # 当前服务的项目是否已经存在在tmp_project中，存在则直接取用
            if last_project.get(service.project_key):
                project = last_project.get(service.project_key)
            else:
                project = (
                    ProjectHandler().all_project.filter(key=service.project_key).first()
                )
                last_project[service.project_key] = project

            # 数据结构构造
            service_dict["service_name"] = service_name
            service_dict["service_desc"] = service_desc
            service_dict["project_name"] = project.name
            recent_service.append(service_dict)
        return recent_service
