# -*- coding: utf-8 -*-
# @Time        :2025/5/28 9:10
# @Author      :文刀水寿
# @File        : signals.py
"""
 @Description :
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps


@receiver(post_save, sender=apps.get_model('App', 'User'))
def my_signal(sender, instance, **kwargs):
    pass
