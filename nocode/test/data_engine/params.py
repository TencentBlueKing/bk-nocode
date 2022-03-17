# -*- coding: utf-8 -*-

CREATE_PROJECT_DATA = {
    "key": "test2",
    "creator": "admin",
    "name": "test",
    "desc": "test",
    "color": [],
    "logo": "T",
}

WORKSHEET_DATA = {
    "creator": "admin",
    "create_at": "2021-09-18 15:51:22",
    "update_at": "2021-09-18 15:51:22",
    "updated_by": "admin",
    "is_deleted": False,
    "name": "test",
    "desc": "test",
    "key": "test",
    "project_key": CREATE_PROJECT_DATA["key"],
}

CREATE_PAGE_1 = {
    "project_key": CREATE_PROJECT_DATA["key"],
    "name": "page1",
    "type": "FUNCTION",
}
CREATE_PAGE_2 = {
    "project_key": CREATE_PROJECT_DATA["key"],
    "name": "page2",
    "type": "LIST",
}
CREATE_PAGE_3 = {
    "project_key": CREATE_PROJECT_DATA["key"],
    "name": "page3",
    "type": "SHEET",
}

SON_POINT = [CREATE_PAGE_1, CREATE_PAGE_2, CREATE_PAGE_3]