# -*- coding: utf-8 -*-
import json

WORKSHEET_DATA = {
    "creator": "admin",
    "create_at": "2021-09-18 15:51:22",
    "update_at": "2021-09-18 15:51:22",
    "updated_by": "admin",
    "is_deleted": False,
    "name": "test",
    "desc": "test_worksheet",
    "key": "test",
    "project_key": "test",
}

CREATE_PROJECT_DATA = {
    "key": "test",
    "creator": "admin",
    "name": "test",
    "desc": "test",
    "color": json.dumps(["#3a84ff", "#6cbaff"]),
    "logo": "T",
}
