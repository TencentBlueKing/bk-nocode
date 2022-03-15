# -*- coding: utf-8 -*-
import json

WORKSHEET_DATA = {
    "creator": "admin",
    "create_at": "2021-09-18 15:51:22",
    "update_at": "2021-09-18 15:51:22",
    "updated_by": "admin",
    "is_deleted": False,
    "name": "test2",
    "desc": "test_worksheet2",
    "key": "test2",
    "project_key": "test2",
}

CREATE_PROJECT_DATA = {
    "key": "test2",
    "creator": "admin",
    "name": "test",
    "desc": "test",
    "color": json.dumps(["#3a84ff", "#6cbaff"]),
    "logo": "T",
}
