# -*- coding: utf-8 -*-

from itsm.project.handler.project_handler import ProjectHandler
from itsm.project.models import Project, ProjectConfig


def project_change_handler(sender, instance, created, *args, **kwargs):
    if not getattr(sender, "change_flag", False):
        return
    if isinstance(instance, Project):
        project = instance

    if isinstance(instance, ProjectConfig):
        project_key = instance.project_key
        project = ProjectHandler(project_key=project_key).instance

    if project.publish_status == "RELEASED":
        project.publish_status = "CHANGED"
        project.save()
