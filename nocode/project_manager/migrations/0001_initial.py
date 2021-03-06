# Generated by Django 3.2.4 on 2021-09-22 20:12

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ProjectVersion",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "creator",
                    models.CharField(
                        blank=True, max_length=64, null=True, verbose_name="创建人"
                    ),
                ),
                (
                    "create_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
                ),
                ("update_at", models.DateTimeField(auto_now=True, verbose_name="更新时间")),
                (
                    "updated_by",
                    models.CharField(
                        blank=True, max_length=64, null=True, verbose_name="修改人"
                    ),
                ),
                (
                    "is_deleted",
                    models.BooleanField(
                        db_index=True, default=False, verbose_name="是否软删除"
                    ),
                ),
                ("project_config", models.JSONField(verbose_name="项目配置")),
                ("page", models.JSONField(verbose_name="项目导航元信息")),
                ("page_component", models.JSONField(verbose_name="页面组件元信息")),
                ("worksheet", models.JSONField(verbose_name="项目工作表元信息")),
                ("worksheet_field", models.JSONField(verbose_name="项目工作表字段元信息")),
                (
                    "version_number",
                    models.CharField(max_length=64, verbose_name="版本号，32位uuid"),
                ),
                (
                    "project_key",
                    models.CharField(default=0, max_length=32, verbose_name="项目key"),
                ),
            ],
        ),
    ]
