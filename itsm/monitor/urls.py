# -*- coding: utf-8 -*-
from django.conf.urls import url

from itsm.monitor.views import healthz

urlpatterns = [
    # main
    url(r"^healthz/$", healthz),
]
