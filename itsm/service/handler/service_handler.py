# -*- coding: utf-8 -*-
from itsm.component.constants import DEFAULT_PROJECT_PROJECT_KEY
from itsm.component.exceptions import ServiceNotExist, ServiceCatalogNotExist
from itsm.project.models import Project
from itsm.service.models import CatalogService, Service, ServiceCatalog, FavoriteService


class CatalogServiceHandler:
    def __init__(self, instance=None, project_key=DEFAULT_PROJECT_PROJECT_KEY):
        self.project_key = project_key
        self.obj = instance
        super(CatalogServiceHandler, self).__init__()

    def _get_instance(self):
        try:
            obj = CatalogService.objects.get(project_key=self.project_key)
        except CatalogService.DoesNotExist:
            raise ServiceNotExist()
        return obj

    @classmethod
    def bind_service_to_catalog(
        cls, service_id, operate_id, project_key=DEFAULT_PROJECT_PROJECT_KEY
    ):
        """绑定服务到目录上，目录已被占用，则返回False"""
        # 目录没有改变
        if CatalogService.objects.filter(
            service_id=service_id, catalog_id=operate_id
        ).exists():
            return {"result": True, "message": "目录没有改变，无需重复绑定"}

        # 解除服务和其他目录的绑定
        CatalogService.objects.filter(service_id=service_id).delete()
        obj, created = CatalogService.objects.update_or_create(
            service_id=service_id, catalog_id=operate_id, project_key=project_key
        )

        return {"result": True, "created": created, "message": "目录绑定成功"}

    def get_service_operate_type(self, service_id):
        try:
            item_id = CatalogService.objects.get(service_id=service_id).catalog_id
            operate_type = ServiceCatalog.objects.get(pk=item_id).name
        except Exception:
            return ""
        return operate_type


class ServiceHandler:
    def __init__(
        self, instance=None, service_id=None, project_key=DEFAULT_PROJECT_PROJECT_KEY
    ):
        self.project_key = project_key
        self.obj = instance
        self.pk = service_id
        super(ServiceHandler, self).__init__()

    def _get_instance(self):
        try:
            if self.pk:
                obj = Service._objects.get(pk=self.pk)
            else:
                obj = Service._objects.get(project_key=self.project_key, pk=self.pk)
        except Service.DoesNotExist:
            raise ServiceNotExist()
        return obj

    @property
    def instance(self):
        if self.obj is None:
            self.obj = self._get_instance()
        return self.obj

    @property
    def all_service(self):
        return Service.objects.all()

    def filter(self, *args, **kwargs):
        return self.all_service.filter(*args, **kwargs)

    def bind_operate_catalog(self, operate_id):
        """绑定服务到操作目录上"""

        if operate_id is None:
            return {"result": False, "message": "目录不能为空"}

        return CatalogServiceHandler.bind_service_to_catalog(
            self.instance.id, operate_id, self.project_key
        )

    def get_service_operate_type(self, service_id):
        return CatalogServiceHandler().get_service_operate_type(service_id)

    def get_relate_project(self):
        return Project.objects.get(key=self.instance.project_key)

    def service_change_project_change(self):
        project = self.get_relate_project()
        if project.publish_status == "RELEASED":
            project.publish_status = "CHANGED"
            project.save()

    @classmethod
    def filter_by_worksheet(cls, queryset, worksheet_name, project_key):
        """
        根据表单名称反向查询功能
        """
        from itsm.service.handler.worksheet_handler import WorksheetHandler

        if not worksheet_name:
            return queryset
        worksheet_list = (
            WorksheetHandler()
            .filter(name__icontains=worksheet_name, project_key=project_key)
            .values_list("id", flat=True)
        )
        queryset_obj = queryset.none()
        for worksheet_id in worksheet_list:
            item = queryset.filter(worksheet_ids__icontains=worksheet_id)
            queryset_obj = queryset_obj | item
        return queryset_obj


class ServiceCatalogHandler:
    def __init__(
        self,
        instance=None,
        operate_type=None,
        project_key=DEFAULT_PROJECT_PROJECT_KEY,
        **kwargs
    ):

        self.project_key = project_key
        self.operate_type = operate_type
        if operate_type == "DETAIL":
            self.operate_type = "INFO"
        if operate_type == "EXPORT":
            self.operate_type = "OUTPUT"
        self.obj = instance
        self.kwargs = kwargs
        super(ServiceCatalogHandler, self).__init__()

    def _get_instance(self):
        try:
            if self.project_key and self.operate_type:
                key = "{0}_{1}".format(self.project_key, self.operate_type)
                obj = ServiceCatalog.objects.get(
                    project_key=self.project_key,
                    key=key,
                )
            else:
                obj = ServiceCatalog.objects.filter(project_key=self.project_key)
        except ServiceCatalog.DoesNotExist:
            raise ServiceCatalogNotExist()
        return obj

    @property
    def instance(self):
        if self.obj is None:
            self.obj = self._get_instance()
        return self.obj

    @property
    def exist(self):
        return True if self.instance else False


class FavouriteServiceHandler:
    def __init__(self, instance=None, service_id=None):
        self.obj = instance
        self.pk = service_id
        super(FavouriteServiceHandler, self).__init__()

    def _get_instance(self):
        try:
            obj = FavoriteService.objects.get(pk=self.pk)
        except FavoriteService.DoesNotExist:
            obj = None
        return obj

    @property
    def instance(self):
        if self.obj is None:
            self.obj = self._get_instance()
        return self.obj

    @property
    def all_favourite_service(self):
        return FavoriteService.objects.all()

    def get_all_service(self, username):
        return self.all_favourite_service.filter(user=username).values_list(
            "service_id", flat=True
        )
