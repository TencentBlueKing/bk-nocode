# -*- coding: utf-8 -*-
import jinja2

jj_env = jinja2.Environment(variable_start_string="{", variable_end_string="}")


def render_string(tmpl, context):
    return jj_env.from_string(tmpl).render(**context)
