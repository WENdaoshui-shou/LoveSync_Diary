# -*- coding: utf-8 -*-
# @Time        :2025/5/28 8:09
# @Author      :文刀水寿
# @File        : form.py
"""
 @Description :
"""
from django import forms
from .models import Profile
from .models import Photo


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'userAvatar', 'name', 'gender', 'birth_date', 'location', 'bio',
            'notification_sound', 'vibration_enabled', 'do_not_disturb',
            'comment_notifications', 'like_notifications',
            'profile_visibility', 'show_online_status', 'allow_search',
            'moments_visibility', 'allow_stranger_messages',
            'theme_color', 'font_size', 'interface_style',
            'couple_name', 'couple_avatar', 'love_declaration', 'couple_anniversary',
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 3}),
            'couple_anniversary': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 为所有字段添加统一的样式类
        for field in self.fields:
            if field in ['gender']:  # 单选按钮
                self.fields[field].widget.attrs.update({'class': 'form-radio'})
            elif field in ['notification_sound', 'vibration_enabled', 'do_not_disturb',
                           'comment_notifications', 'like_notifications',
                           'show_online_status', 'allow_search',
                           'allow_stranger_messages']:  # 开关控件
                self.fields[field].widget.attrs.update({'class': 'form-checkbox'})
            else:
                self.fields[field].widget.attrs.update({'class': 'form-input-focus'})


class PhotoUploadForm(forms.ModelForm):
    """照片上传表单"""

    class Meta:
        model = Photo
        fields = ['image', 'description']
