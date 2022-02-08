# -*- coding: utf-8 -*-
from nocode.worksheet.handlers.worksheet_handler import WorkSheetModelHandler


class WorksheetHandler(WorkSheetModelHandler):
    def get_relate_worksheet(self, worksheet_list):
        worksheet_name_list = self.filter(id__in=worksheet_list).values(
            "id", "name", "key"
        )
        item_list = []
        for item in worksheet_name_list:
            item_list.append(
                {"id": item["id"], "name": item["name"], "key": item["key"]}
            )
        return item_list
