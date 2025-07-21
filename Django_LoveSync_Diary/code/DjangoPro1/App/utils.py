# -*- coding: utf-8 -*-
# @Time        :2025/7/10 17:33
# @Author      :文刀水寿
# @File        : utils.py
"""
 @Description :
"""
import random
import string
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont


# 随机生成验证码文本（4位字符）
def generate_verify_code(length=4):
    chars = string.ascii_letters + string.digits  # 包含大小写字母和数字
    return ''.join(random.choice(chars) for _ in range(length))


# 生成验证码图片
def create_verify_image(code, width=120, height=40):
    # 创建图片对象
    image = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(image)

    # 设置字体（
    try:
        font = ImageFont.truetype('static/fonts/simhei.ttf', 28)  # 黑体字体
    except:
        font = ImageFont.load_default()  # 默认字体

    # 绘制验证码文本
    for i, char in enumerate(code):
        # 随机颜色和位置
        color = (random.randint(30, 100), random.randint(30, 100), random.randint(30, 100))
        position = (10 + i * 25, random.randint(5, 10))
        draw.text(position, char, font=font, fill=color)

    # 绘制干扰线
    for _ in range(5):
        color = (random.randint(60, 180), random.randint(60, 180), random.randint(60, 180))
        draw.line(
            [
                (random.randint(0, width), random.randint(0, height)),
                (random.randint(0, width), random.randint(0, height))
            ],
            fill=color,
            width=2
        )

    # 绘制噪点
    for _ in range(30):
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        draw.point(
            (random.randint(0, width), random.randint(0, height)),
            fill=color
        )

    # 保存图片到内存
    buffer = BytesIO()
    image.save(buffer, 'PNG')
    buffer.seek(0)
    return buffer
