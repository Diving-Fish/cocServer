import asyncio
import base64
from io import BytesIO

from PIL import ImageFont, ImageDraw, Image
import numpy as np
from nonebot import CommandSession, on_command
import re
import aiohttp

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
    draw.rectangle((x + offset_x - 2, 360, x + 2 + width + offset_x, 360 + height * 1.2), fill=(0, 0, 0, 255))
    draw.text((x + offset_x, 360), text, font=font, fill=(255, 255, 255, 255))


def image_to_base64(img):
    output_buffer = BytesIO()
    img.save(output_buffer, format='PNG')
    byte_data = output_buffer.getvalue()
    base64_str = base64.b64encode(byte_data)
    return base64_str


@on_command('high_eq', patterns='低情商.+高情商.+', only_to_me=False)
async def high_eq(session: CommandSession):
    regex = '低情商(.+)高情商(.+)'
    groups = re.match(regex, session.current_arg_text).groups()
    left = groups[0].strip()
    right = groups[1].strip()
    if len(left) > 15 or len(right) > 15:
        await session.send("为了图片质量，请不要多于15个字符")
        return
    img_p = Image.open('high_eq_image.png')
    draw_text(img_p, left, 0)
    draw_text(img_p, right, 400)
    await session.send([{
        "type": "image",
        "data": {
            "file": f"base64://{str(image_to_base64(img_p), encoding='utf-8')}"
        }
    }])


async def get_jlpx(jl, px, bottom):
    data = {
        'id': jl,
        'zhenbi': '20191123',
        'id1': '9007',
        'id2': '18',
        'id3':  '#0000FF',
        'id4':  '#FF0000',
        'id5': '10',
        'id7': bottom,
        'id8': '9005',
        'id10': px,
        'id11': 'jiqie.com_2',
        'id12': '241'
    }
    async with aiohttp.request(method='POST', url="http://jiqie.zhenbi.com/e/re111.php", data=data) as resp:
        t = await resp.text()
        regex = '<img src="(.+)">'
        return re.match(regex, t).groups()[0]


@on_command('金龙盘旋', only_to_me=False, shell_like=True)
async def jlpx(session: CommandSession):
    if len(session.args['argv']) != 3:
        await session.send("金龙盘旋需要三个参数")
    url = await get_jlpx(session.args['argv'][0], session.args['argv'][1], session.args['argv'][2])
    await session.send([{
        "type": "image",
        "data": {
            "file": f"{url}"
        }
    }])