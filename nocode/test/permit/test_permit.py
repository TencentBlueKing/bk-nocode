# -*- coding: utf-8 -*-

from django.test import TestCase, override_settings
from blueapps.core.celery.celery import app

from itsm.project.models import Project, ProjectConfig
from nocode.test.permit.params import (
    ADD_USER_GROUP,
    ADD_USER,
    PERMIT_DATA,
    CREATE_PROJECT_DATA,
)


class TestPage(TestCase):
    def setUp(self) -> None:
        app.conf.update(CELERY_ALWAYS_EAGER=True)
        ProjectConfig.objects.all().delete()
        Project.objects.all().delete()

        self.project = Project.objects.create(**CREATE_PROJECT_DATA)
        project_config = {"workflow_prefix": "test", "project_key": "test"}
        ProjectConfig.objects.create(**project_config)

    def add_user_group(self):
        url = "/api/permit/user_group/"
        res = self.client.post(url, ADD_USER_GROUP, content_type="application/json")
        self.assertEqual(res.data["code"], "OK")
        self.assertEqual(res.data["message"], "success")
        self.assertEqual(res.data["data"]["project_key"], "test")
        return res.data["data"]

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_add_user_group(self):
        self.add_user_group()

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_list_user_group(self):
        self.add_user_group()
        url = "/api/permit/user_group/?project_key=test"
        res = self.client.get(url)
        self.assertEqual(res.data["code"], "OK")
        self.assertEqual(res.data["message"], "success")
        self.assertEqual(len(res.data["data"]["items"]), 1)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_delete_user_group(self):
        data = self.add_user_group()
        url = "/api/permit/user_group/{}/"
        res = self.client.delete(url.format(data["id"]))
        self.assertEqual(res.data["code"], "OK")
        self.assertEqual(res.data["message"], "success")

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_operate_member_of_user_group(self):
        data = self.add_user_group()
        url = "/api/permit/user_group/{}/"
        data.pop("name")
        data["users"] = ADD_USER
        res = self.client.put(
            url.format(data["id"]), data=data, content_type="application/json"
        )
        self.assertEqual(res.data["code"], "OK")
        self.assertEqual(res.data["message"], "success")

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_set_permit_to_user_group(self):
        data = self.add_user_group()
        data.pop("name")
        url = "/api/permit/user_group/{}/"
        data["action_configs"] = PERMIT_DATA

        res = self.client.put(
            url.format(data["id"]), data=data, content_type="application/json"
        )
        self.assertEqual(res.data["code"], "OK")
        self.assertEqual(res.data["message"], "success")
