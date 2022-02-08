# -*- coding: utf-8 -*-

from django.utils.translation import ugettext as _

from itsm.component.utils.response import Fail

IMAGE_VALIDATE = ["png", "jpg", "jpeg", "svg"]
JPG_FORMAT = ["jpg", "jpeg"]
SVG_FORMAT = "svg"


def image_format_validate(image):
    image_name = image.name
    file_format = image_name.split(".")[-1]
    if file_format.lower() not in IMAGE_VALIDATE:
        raise Fail(message=_("该文件不符合本系统所支持的图片格式")).json()
