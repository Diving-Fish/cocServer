import base64
from io import BytesIO

from PIL import ImageFont, ImageDraw, Image
import numpy as np
from nonebot import CommandSession, on_command
import re

path = 'high_eq_image.png'
fontpath = "msyh.ttc"


def draw_text(img_pil, text, offset_x):
    draw = ImageDraw.Draw(img_pil)
    font = ImageFont.truetype(fontpath, 48)
    width, height = draw.textsize(text, font)
    x = 5
    if width > 390:
        font = ImageFont.truetype(fontpath, int(390 * 48 / width))
        width, height = draw.textsize(text, font)
    else:
        x = int((400 - width) / 2)
    draw.rectangle((x + offset_x - 2, 360, x + 2 + width + offset_x, 360 + height * 1.2), fill=(0, 0, 0, 0))
    draw.text((x + offset_x, 360), text, font=font, fill=(255, 255, 255, 0))


def image_to_base64(img):
    output_buffer = BytesIO()
    img.save(output_buffer, format='PNG')
    byte_data = output_buffer.getvalue()
    base64_str = base64.b64encode(byte_data)
    return base64_str


@on_command('high_eq', patterns='低情商.+高情商.+', only_to_me=False)
def high_eq(session: CommandSession):
    regex = '低情商(.+)高情商(.+)'
    groups = re.match(regex, session.current_arg_text).groups()
    left = groups[0].strip()
    right = groups[1].strip()
    if len(left) > 15 or len(right) > 15:
        session.send("为了图片质量，请不要多于15个字符")
        return
    img_p = Image.open('high_eq_image.png')
    draw_text(img_p, left, 0)
    draw_text(img_p, right, 400)
    session.send([{
        "type": "image",
        "data": {
            "file": f"base64://{image_to_base64(img_p)}"
        }
    }])




