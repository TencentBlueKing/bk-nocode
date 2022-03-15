# -*- coding: utf-8 -*-
import json

from django.test import TestCase, override_settings

from blueapps.core.celery.celery import app

from itsm.project.models import Project, ProjectConfig
from nocode.test.project_manager.params import CREATE_PROJECT_DATA


class TestProjectManager(TestCase):
    def setUp(self) -> None:
        app.conf.update(CELERY_ALWAYS_EAGER=True)
        ProjectConfig.objects.all().delete()
        Project.objects.all().delete()

        Project.objects.get_or_create(**CREATE_PROJECT_DATA)
        project_config = {"workflow_prefix": "test", "project_key": "test"}
        ProjectConfig.objects.create(**project_config)

    def project_publish(self):
        publish_rep = self.client.post(
            path="/api/project/manager/publish/",
            data=json.dumps({"project_key": "test"}),
            content_type="application/json",
        )
        self.assertEqual(publish_rep.data["code"], "OK")
        self.assertEqual(publish_rep.data["message"], "success")
        return publish_rep.data["data"]["task_id"]

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_publish(self):
        self.project_publish()
        project = Project.objects.get(key="test")
        self.assertEqual(project.publish_status, "RELEASED")

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_publish_logs(self):
        task_id = self.project_publish()

        url = f"/api/project/manager/publish_logs/?task_id={task_id}"
        res = self.client.get(url)
        self.assertEqual(res.data["code"], "OK")
        self.assertEqual(res.data["message"], "success")
        self.assertEqual(len(res.data["data"]), 23)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_project_version(self):
        self.project_publish()

        project = Project.objects.get(key="test")
        url = "/api/project/manager/version/"
        data = {
            "project_key": "test",
            "version_number": project.version_number,
        }

        res = self.client.post(url, data=data, content_type="application/json")
        self.assertEqual(res.data["message"], "success")
        self.assertEqual(res.data["code"], "OK")
        self.assertEqual(res.data["data"]["version_number"], project.version_number)
