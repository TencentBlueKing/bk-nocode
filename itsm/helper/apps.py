# -*- coding: utf-8 -*-
import datetime

from django.apps import AppConfig
from django.db import connection

import pipeline


class HelperConfig(AppConfig):
    name = "itsm.helper"

    def is_pipeline_ready(self):
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT `app`, `name` FROM django_migrations where app='pipeline';"
                )
                rows = cursor.fetchall()
                if len(rows) > 0:
                    return True
                else:
                    return False
        except Exception:
            return False

    def ready(self):
        # 全新部署
        print("fix pipeline update")
        migrations = (
            ("engine", "0017_auto_20190719_1010"),
            ("engine", "0018_auto_20190729_1041"),
            ("engine", "0019_auto_20190729_1044"),
            ("engine", "0020_pipelinemodel_priority"),
            ("engine", "0021_auto_20191213_0725"),
            ("engine", "0022_scheduleservice_multi_callback_enabled"),
            ("engine", "0023_status_state_refresh_at"),
            ("engine", "0024_auto_20200224_0308"),
            ("engine", "0025_multicallbackdata"),
            ("engine", "0026_auto_20200610_1442"),
            ("engine", "0027_sendfailedcelerytask"),
            ("pipeline", "0020_auto_20190906_1119"),
            ("pipeline", "0021_auto_20190906_1143"),
            ("pipeline", "0022_pipelineinstance_is_revoked"),
        )
        if pipeline.__version__ != "2.4.3":
            # 如果版本号不是2.4.3, 说明是升级的pipline
            # 去DB里面查询是不是已经升级过了
            if not self.is_pipeline_ready():
                return
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT `app`, `name` FROM django_migrations;")
                    rows = cursor.fetchall()
                    for migration in migrations:
                        if migration in rows:
                            continue
                        dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                        cursor.execute(
                            'INSERT INTO `django_migrations` (`app`, `name`, `applied`) VALUES ("{}", "{}", "{}");'.format(  # noqa
                                migration[0], migration[1], dt
                            )
                        )
            except Exception as e:
                print("修复pipline 逻辑失败，错误信息: error = {}".format(e))
