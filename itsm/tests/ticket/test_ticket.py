# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.

Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.

BK-ITSM 蓝鲸流程服务 is licensed under the MIT License.

License for BK-ITSM 蓝鲸流程服务:
--------------------------------------------------------------------
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial
portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

__author__ = "蓝鲸智云"
__copyright__ = "Copyright © 2012-2020 Tencent BlueKing. All Rights Reserved."

import json
import mock
from blueapps.core.celery.celery import app

from django.test import TestCase, override_settings
from django.core.cache import cache

from itsm.project.models import ProjectConfig, Project
from itsm.tests.ticket.params import CREATE_TICKET_PARAMS
from itsm.ticket.models import Ticket, Status, AttentionUsers
from itsm.component.constants import APPROVAL_STATE


class TicketTest(TestCase):
    def setUp(self):
        app.conf.update(CELERY_ALWAYS_EAGER=True)
        Ticket.objects.all().delete()
        AttentionUsers.objects.all().delete()
        self.create_project_data = {
            "key": "0",
            "name": "test",
            "logo": "",
            "color": [],
            "creator": "admin",
            "create_at": "2021-05-30 17:16:40",
            "updated_by": "test_admin",
            "update_at": "2021-05-30 17:16:40",
        }
        Project.objects.create(**self.create_project_data)
        project_config = {"workflow_prefix": "test", "project_key": "0"}
        ProjectConfig.objects.create(**project_config)

    def project_publish(self):
        publish_rep = self.client.post(
            path="/api/project/manager/publish/",
            data=json.dumps({"project_key": "0"}),
            content_type="application/json",
        )
        self.assertEqual(publish_rep.data["code"], "OK")
        self.assertEqual(publish_rep.data["message"], "success")

    def create_ticket(self):
        self.project_publish()
        url = "/api/ticket/receipts/create_ticket/"
        rsp = self.client.post(
            path=url,
            data=json.dumps(CREATE_TICKET_PARAMS),
            content_type="application/json",
        )
        self.assertEqual(rsp.data["code"], "OK")
        self.assertEqual(rsp.data["message"], "success")
        ticket_id = rsp.data["data"]["id"]
        return ticket_id

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_create_ticket(self):
        self.create_ticket()

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.role.models.get_user_departments")
    def test_list(self, patch_get_user_departments):
        patch_get_user_departments.return_value = {}

        ticket_id = self.create_ticket()
        url = "/api/ticket/receipts/"
        list_rsp = self.client.get(url)
        self.assertEqual(list_rsp.data["code"], "OK")
        self.assertEqual(list_rsp.data["message"], "success")
        self.assertEqual(ticket_id, list_rsp.data["data"]["items"][0]["id"])
        self.assertEqual(1, len(list_rsp.data["data"]["items"]))
        # self.assertEqual(["test"], list_rsp.data["data"]["items"][0]["followers"])
        self.assertEqual(ticket_id, list_rsp.data["data"]["items"][0]["id"])

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.ticket.serializers.ticket.get_bk_users")
    @mock.patch("itsm.component.utils.misc.get_bk_users")
    def test_retrieve(self, patch_misc_get_bk_users, path_get_bk_users):
        patch_misc_get_bk_users.return_value = {}
        path_get_bk_users.return_value = {}

        ticket_id = self.create_ticket()
        get_url = "/api/ticket/receipts/{}/".format(ticket_id)
        list_rsp = self.client.get(get_url)
        self.assertEqual(list_rsp.data["code"], "OK")
        self.assertEqual(list_rsp.data["message"], "success")
        self.assertEqual([], list_rsp.data["data"]["followers"])
        self.assertEqual(ticket_id, list_rsp.data["data"]["id"])

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.ticket.serializers.ticket.get_bk_users")
    @mock.patch("itsm.component.utils.misc.get_bk_users")
    def test_add_follower(self, patch_misc_get_bk_users, path_get_bk_users):
        patch_misc_get_bk_users.return_value = {}
        path_get_bk_users.return_value = {}

        ticket_id = self.create_ticket()

        add_url = "/api/ticket/receipts/{}/add_follower/".format(ticket_id)
        add_rsp = self.client.post(
            path=add_url,
            data=json.dumps({"attention": True}),
            content_type="application/json",
        )
        self.assertEqual(add_rsp.data["code"], "OK")
        self.assertEqual(add_rsp.data["message"], "success")
        get_url = "/api/ticket/receipts/{}/".format(ticket_id)
        list_rsp = self.client.get(get_url)
        self.assertEqual(list_rsp.data["code"], "OK")
        self.assertEqual(list_rsp.data["message"], "success")
        self.assertEqual(["admin"], list_rsp.data["data"]["followers"])
        self.assertEqual(ticket_id, list_rsp.data["data"]["id"])

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.ticket.serializers.ticket.get_bk_users")
    @mock.patch("itsm.component.utils.misc.get_bk_users")
    def test_delete_follower(self, patch_misc_get_bk_users, path_get_bk_users):
        patch_misc_get_bk_users.return_value = {}
        path_get_bk_users.return_value = {}
        ticket_id = self.create_ticket()

        add_url = "/api/ticket/receipts/{}/add_follower/".format(ticket_id)
        add_rsp = self.client.post(
            path=add_url,
            data=json.dumps({"attention": False}),
            content_type="application/json",
        )
        self.assertEqual(add_rsp.data["code"], "OK")
        self.assertEqual(add_rsp.data["message"], "success")
        get_url = "/api/ticket/receipts/{}/".format(ticket_id)
        list_rsp = self.client.get(get_url)
        self.assertEqual(list_rsp.data["code"], "OK")
        self.assertEqual(list_rsp.data["message"], "success")
        self.assertEqual([], list_rsp.data["data"]["followers"])
        self.assertEqual(ticket_id, list_rsp.data["data"]["id"])

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    @mock.patch("itsm.ticket.serializers.ticket.get_bk_users")
    @mock.patch("itsm.component.utils.misc.get_bk_users")
    def test_operate(self, patch_misc_get_bk_users, path_get_bk_users):
        patch_misc_get_bk_users.return_value = {}
        path_get_bk_users.return_value = {}

        ticket_id = self.create_ticket()
        AttentionUsers.objects.create(ticket_id=ticket_id, follower="test")

        get_url = "/api/ticket/receipts/{}/".format(ticket_id)
        list_rsp = self.client.get(get_url)
        self.assertEqual(list_rsp.data["code"], "OK")
        self.assertEqual(list_rsp.data["message"], "success")
        self.assertEqual(["test"], list_rsp.data["data"]["followers"])
        self.assertEqual(ticket_id, list_rsp.data["data"]["id"])
        self.assertEqual(True, list_rsp.data["data"]["can_view"])
        self.assertEqual(False, list_rsp.data["data"]["can_operate"])

    @mock.patch.object(Status, "approval_result")
    @mock.patch.object(Status, "get_processor_in_sign_state")
    @mock.patch.object(Ticket, "activity_callback")
    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_batch_approval_add_queue_success(
        self, mock_callback, mock_user, mock_result
    ):
        mock_callback.return_value = type("MyResult", (object,), {"result": True})
        mock_user.return_value = "admin"
        mock_result.return_value = [
            {"id": 1, "key": "123", "value": "true"},
            {"id": 2, "key": "234", "value": "通过"},
        ]
        ticket = Ticket.objects.create(
            sn="123", title="test", service_id="456", service_type="change"
        )
        status = Status.objects.create(
            ticket_id=ticket.id, state_id="111", status="RUNNING", type=APPROVAL_STATE
        )
        ticket.node_status.add(status)
        data = {
            "result": "true",
            "opinion": "xxxxx",
            "approval_list": [{"ticket_id": ticket.id}],
        }
        url = "/api/ticket/receipts/batch_approval/"
        rsp = self.client.post(
            path=url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(
            cache.get("approval_status_{}_{}_{}".format("admin", ticket.id, "111")),
            "RUNNING",
        )

    @mock.patch.object(Status, "approval_result")
    @mock.patch.object(Status, "get_processor_in_sign_state")
    @mock.patch.object(Ticket, "activity_callback")
    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_batch_approval_add_queue_error(
        self, mock_callback, mock_user, mock_result
    ):
        mock_callback.return_value = type(
            "MyResult", (object,), {"result": False, "message": "error_test"}
        )
        mock_user.return_value = "admin"
        mock_result.return_value = [
            {"id": 1, "key": "123", "value": "true"},
            {"id": 2, "key": "234", "value": "通过"},
        ]
        ticket = Ticket.objects.create(
            sn="123", title="test", service_id="456", service_type="change"
        )
        status = Status.objects.create(
            ticket_id=ticket.id, state_id="111", status="RUNNING", type=APPROVAL_STATE
        )
        ticket.node_status.add(status)
        data = {
            "result": "true",
            "opinion": "xxxxx",
            "approval_list": [{"ticket_id": ticket.id}],
        }
        url = "/api/ticket/receipts/batch_approval/"
        rsp = self.client.post(
            path=url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(
            cache.get("approval_status_{}_{}_{}".format("admin", ticket.id, "111")),
            None,
        )
