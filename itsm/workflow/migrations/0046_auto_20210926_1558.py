# Generated by Django 3.2.4 on 2021-09-26 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("workflow", "0045_auto_20210621_1206"),
    ]

    operations = [
        migrations.AlterField(
            model_name="defaultfield",
            name="source_type",
            field=models.CharField(
                choices=[
                    ("CUSTOM", "自定义数据"),
                    ("API", "接口数据"),
                    ("DATADICT", "数据字典"),
                    ("RPC", "系统数据"),
                    ("WORKSHEET", "工作表"),
                ],
                default="CUSTOM",
                max_length=32,
                verbose_name="数据来源类型",
            ),
        ),
        migrations.AlterField(
            model_name="field",
            name="source_type",
            field=models.CharField(
                choices=[
                    ("CUSTOM", "自定义数据"),
                    ("API", "接口数据"),
                    ("DATADICT", "数据字典"),
                    ("RPC", "系统数据"),
                    ("WORKSHEET", "工作表"),
                ],
                default="CUSTOM",
                max_length=32,
                verbose_name="数据来源类型",
            ),
        ),
        migrations.AlterField(
            model_name="taskfieldschema",
            name="source_type",
            field=models.CharField(
                choices=[
                    ("CUSTOM", "自定义数据"),
                    ("API", "接口数据"),
                    ("DATADICT", "数据字典"),
                    ("RPC", "系统数据"),
                    ("WORKSHEET", "工作表"),
                ],
                default="CUSTOM",
                max_length=32,
                verbose_name="数据来源类型",
            ),
        ),
        migrations.AlterField(
            model_name="templatefield",
            name="source_type",
            field=models.CharField(
                choices=[
                    ("CUSTOM", "自定义数据"),
                    ("API", "接口数据"),
                    ("DATADICT", "数据字典"),
                    ("RPC", "系统数据"),
                    ("WORKSHEET", "工作表"),
                ],
                default="CUSTOM",
                max_length=32,
                verbose_name="数据来源类型",
            ),
        ),
    ]
