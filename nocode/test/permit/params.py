# -*- coding: utf-8 -*-
import json

ADD_USER_GROUP = {"name": "test_user_group", "desc": "test", "project_key": "test"}

ADD_USER = {"departments": [], "members": ["admin"]}

PERMIT_DATA = {
    "page_view": [{"id": 1, "name": "test"}],
    "action_execute": [
        {"id": 21, "name": "test", "actions": [{"id": 36, "name": "test"}]}
    ],
}

CREATE_PROJECT_DATA = {
    "key": "test",
    "creator": "admin",
    "name": "test",
    "desc": "test",
    "color": json.dumps(["#3a84ff", "#6cbaff"]),
    "logo": "T",
}
