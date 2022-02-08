# -*- coding: utf-8 -*-
from .resources import CollectionsAPI

# 判断是否在Django环境下，如果在Django环境下，默认从settings中读取配置信息，否则，使用默认配置
# 客户端可采用import后再修改的方式来改变配置
try:
    from django.conf import settings

    APP_CODE = settings.APP_CODE
    SECRET_KEY = settings.SECRET_KEY
except Exception:
    APP_CODE = None
    SECRET_KEY = None

AVAILABLE_COLLECTIONS = {
    "iam": CollectionsAPI,
}
