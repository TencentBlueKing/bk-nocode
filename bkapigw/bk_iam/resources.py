# -*- coding: utf-8 -*-
from django.conf import settings

from .base import RequestAPI


class CollectionsAPI(object):
    def __init__(self, client):
        self.client = client
        self.host = settings.IAM_GW_HOST

        self.create_user_group = RequestAPI(
            client=self.client,
            method="POST",
            host=self.host,
            path="/api/v1/open/management/grade_managers/{id}/groups/",
        )

        self.create_user_group_policies = RequestAPI(
            client=self.client,
            method="POST",
            host=self.host,
            path="/api/v1/open/management/groups/{id}/policies/",
        )

        self.add_user_group_members = RequestAPI(
            client=self.client,
            method="POST",
            host=self.host,
            path="/api/v1/open/management/groups/{id}/members/",
        )

        self.delete_user_group = RequestAPI(
            client=self.client,
            method="DELETE",
            host=self.host,
            path="/api/v1/open/management/groups/{id}/",
        )

        self.grade_managers = RequestAPI(
            client=self.client,
            method="POST",
            host=self.host,
            path="/api/v1/open/management/grade_managers/",
        )

        self.get_user_group = RequestAPI(
            client=self.client,
            method="GET",
            host=self.host,
            path="/api/v1/open/management/grade_managers/{id}/groups?limit=100",
        )

        self.get_user_group_members = RequestAPI(
            client=self.client,
            method="GET",
            host=self.host,
            path="/api/v1/open/management/groups/{id}/members/",
        )

        self.delete_user_group_members = RequestAPI(
            client=self.client,
            method="DELETE",
            host=self.host,
            path="/api/v1/open/management/groups/{id}/members?type={type}&ids={ids}",
        )
