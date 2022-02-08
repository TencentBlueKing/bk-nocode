# -*- coding: utf-8 -*-
from nocode.page.handlers.page_handler import PageComponentHandler, PageModelHandler


class PageComponentHandler(PageComponentHandler):
    def get_component_by_service(self, service_id):

        return list(
            self.filter(
                value=service_id, type__in=["FUNCTION", "LIST", "SHEET"]
            ).values_list("page_id", flat=True)
        )

    def get_relate_page(self, service_id):
        page_ids = self.get_component_by_service(service_id)
        page_names = (
            PageModelHandler().filter(pk__in=page_ids).values_list("name", flat=True)
        )
        return list(page_names)


class PageModelHandler(PageModelHandler):
    pass
