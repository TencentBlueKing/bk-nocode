# -*- coding: utf-8 -*-
import re

from django.core.validators import RegexValidator
from django.utils.translation import ugettext as _


prefix_validator = RegexValidator(
    re.compile("^[a-zA-Z]+$"), message=_("请输入合法编码：英文及下划线"), code="invalid"
)
