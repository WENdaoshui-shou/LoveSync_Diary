# -*- coding: utf-8 -*-
# @Time        :2025/5/13 17:58
# @Author      :文刀水寿
# @File        : jinja2_env.py
"""
 @Description :
"""
from jinja2 import Environment, FileSystemLoader
from django.urls import reverse
from django.templatetags.static import static


# 创建 Jinja2 环境对象
def environment(**options):
    env = Environment(**options)
    env.globals.update({
        'static': static,
        'url': reverse,
    })
    return env