# -*- coding: utf-8 -*-
from itsm.project.execptions import DeleteCollectionError
from nocode.page.models import PageComponentCollection


class PageComponentCollectionHandler:
    def __init__(self, project_key):
        self.project_key = project_key

    def delete_collection_history(self):
        try:
            PageComponentCollection.objects.filter(
                project_key=self.project_key
            ).delete()
        except Exception:
            raise DeleteCollectionError()
