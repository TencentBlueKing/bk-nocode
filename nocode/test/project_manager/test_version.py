import json
import mock

from django.test import TestCase, override_settings
from blueapps.core.celery.celery import app

from itsm.project.handler.permit_engine_handler import PermitInitManagerDispatcher
from itsm.project.models import ServiceCatalog

from itsm.project.models import Project, ProjectConfig
from itsm.tests.project.params import CREATE_PROJECT_DATA
from nocode.page.models import Page
from nocode.test.page.params import SON_POINT
from nocode.test.worksheet.params import WORKSHEET_DATA
from nocode.worksheet.handlers.moudule_handler import ServiceHandler, DjangoHandler
from nocode.worksheet.models import WorkSheet


class TestProjectManager(TestCase):
    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch.object(PermitInitManagerDispatcher, "init_permit")
    @mock.patch.object(ServiceHandler, "init_service")
    @mock.patch.object(DjangoHandler, "init_db")
    @mock.patch.object(ServiceHandler, "migrate_service")
    def setUp(self, mock_result, mock_back, mock_callback, mock_data) -> None:
        app.conf.update(CELERY_ALWAYS_EAGER=True)
        ProjectConfig.objects.all().delete()
        Project.objects.all().delete()

        mock_result.return_value = 1
        mock_back.return_value = {}
        mock_callback.return_value = {}
        mock_data.return_value = {}
        self.create_project()
        self.page_id = self.page_batch_save()
        self.worksheet_id = self.field_batch_save()
        self.project_publish()

    def create_project(self):
        resp = self.client.post(
            "/api/project/projects/",
            {},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["result"], False)
        self.assertEqual(resp.data["code"], "VALIDATE_ERROR")

        resp = self.client.post(
            "/api/project/projects/",
            json.dumps(CREATE_PROJECT_DATA),
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data["result"], True)

        service_catalog = len(
            ServiceCatalog.objects.filter(project_key=CREATE_PROJECT_DATA["key"])
        )

        self.assertEqual(service_catalog, 7)

        self.assertEqual(
            ProjectConfig.objects.filter(
                project_key=CREATE_PROJECT_DATA["key"]
            ).exists(),
            True,
        )

    def page_batch_save(self):
        root = Page.objects.get(key="root", project_key=CREATE_PROJECT_DATA["key"])
        for point in SON_POINT:
            point.setdefault("parent_id", root.id)
            resp = self.client.post("/api/page_design/page/", point)
            self.assertEqual(resp.data["result"], True)

        page = Page.objects.get(name="page1", type="FUNCTION")
        data = {
            "page_id": page.id,
            "components": [
                {
                    "page_id": page.id,
                    "type": "FUNCTION",
                    "value": 29,
                    "config": {"name": "test", "desc": "test"},
                }
            ],
        }

        res = self.client.post(
            "/api/page_design/page_component/batch_save/",
            data,
            content_type="application/json",
        )
        self.assertEqual(res.data["result"], True)
        self.assertEqual(res.data["message"], "success")
        self.assertEqual(len(res.data["data"]), 1)
        return page.id

    def field_batch_save(self):
        worksheet = WorkSheet.objects.create(**WORKSHEET_DATA)

        worksheet_field = {
            "worksheet_id": worksheet.id,
            "fields": [
                {
                    "meta": {},
                    "api_info": {},
                    "choice": [],
                    "kv_relation": {},
                    "key": "shu_zi_1",
                    "name": "数字1",
                    "desc": "",
                    "type": "INT",
                    "layout": "COL_12",
                    "validate_type": "OPTION",
                    "source_type": "CUSTOM",
                    "api_instance_id": 0,
                    "default": "0",
                    "worksheet_id": worksheet.id,
                    "regex": "EMPTY",
                },
                {
                    "meta": {},
                    "api_info": {},
                    "choice": [],
                    "kv_relation": {},
                    "create_at": "2022-01-27 15:37:28",
                    "key": "shu_zi_2",
                    "name": "数字2",
                    "desc": "",
                    "type": "INT",
                    "layout": "COL_12",
                    "validate_type": "OPTION",
                    "source_type": "CUSTOM",
                    "api_instance_id": 0,
                    "default": "0",
                    "worksheet_id": worksheet.id,
                    "regex": "EMPTY",
                },
            ],
        }
        url = "/api/worksheet/fields/batch_save/"
        res = self.client.post(
            url, data=worksheet_field, content_type="application/json"
        )
        self.assertEqual(res.data["result"], True)
        self.assertEqual(res.data["message"], "success")
        self.assertEqual(len(res.data["data"]), 2)
        return worksheet.id

    def project_publish(self):
        publish_rep = self.client.post(
            path="/api/project/manager/publish/",
            data=json.dumps({"project_key": "test"}),
            content_type="application/json",
        )
        self.assertEqual(publish_rep.data["code"], "OK")
        self.assertEqual(publish_rep.data["message"], "success")

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_project_version(self):
        project = Project.objects.get(key=CREATE_PROJECT_DATA["key"])
        version_config_url = (
            "/api/project/version/project_config/"
            "?project_key={project_key}&version_number={version_number}"
        )
        res = self.client.get(
            version_config_url.format(
                project_key=project.key, version_number=project.version_number
            )
        )
        self.assertEqual(res.data["result"], True)
        self.assertEqual(res.data["message"], "success")
        self.assertEqual(len(res.data["data"]), 3)
        self.assertEqual(res.data["data"]["project_key"], "test")

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_page_version(self):
        project = Project.objects.get(key=CREATE_PROJECT_DATA["key"])
        version_page_url = "/api/project/version/page/?project_key={project_key}&version_number={version_number}"
        res = self.client.get(
            version_page_url.format(
                project_key=project.key, version_number=project.version_number
            )
        )
        self.assertEqual(res.data["result"], True)
        self.assertEqual(res.data["message"], "success")
        self.assertEqual(len(res.data["data"]["children"]), 3)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_component_version(self):
        project = Project.objects.get(key=CREATE_PROJECT_DATA["key"])
        version_component_url = (
            "/api/project/version/page_component/"
            "?project_key={project_key}"
            "&version_number={version_number}&page_id={page_id}"
        )
        res = self.client.get(
            version_component_url.format(
                project_key=project.key,
                version_number=project.version_number,
                page_id=self.page_id,
            )
        )
        self.assertEqual(res.data["result"], True)
        self.assertEqual(res.data["message"], "success")
        self.assertEqual(res.data["data"][0]["page_id"], self.page_id)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_worksheet_version(self):
        project = Project.objects.get(key=CREATE_PROJECT_DATA["key"])
        version_worksheet_url = (
            "/api/project/version/worksheet/"
            "?project_key={project_key}&version_number={version_number}"
        )
        res = self.client.get(
            version_worksheet_url.format(
                project_key=project.key,
                version_number=project.version_number,
            )
        )
        self.assertEqual(res.data["result"], True)
        self.assertEqual(res.data["message"], "success")
        self.assertEqual(len(res.data["data"]), 1)

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_worksheet_fields_version(self):
        project = Project.objects.get(key=CREATE_PROJECT_DATA["key"])
        version_field_url = (
            "/api/project/version/worksheet_field/"
            "?project_key={project_key}&version_number={version_number}&worksheet_id={worksheet_id}"
        )
        res = self.client.get(
            version_field_url.format(
                project_key=project.key,
                version_number=project.version_number,
                worksheet_id=self.worksheet_id,
            )
        )
        self.assertEqual(res.data["result"], True)
        self.assertEqual(res.data["message"], "success")
        self.assertEqual(len(res.data["data"]), 2)
