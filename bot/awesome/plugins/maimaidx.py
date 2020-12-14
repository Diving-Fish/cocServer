from nonebot import on_command, CommandSession, argparse
import requests
import json
import random
import re
from urllib import parse

music_data = requests.get("https://www.diving-fish.com/api/maimaidxprober/music_data").text
music_data = json.loads(music_data)


def random_music(data) -> dict:
    return data[random.randrange(0, len(data))]


async def send_song(session: CommandSession, music: dict):
    if music['type'] == 'SD':
        t = '[标准]'
    else:
        t = '[DX]'
    file = f"https://www.diving-fish.com/covers/{parse.quote(music['title'])}.jpg"
    print(file)
    await session.send([
        {
            "type": "text",
            "data": {
                "text": f"{t}{music['title']}\n"
            }
        },
        {
            "type": "image",
            "data": {
                "file": f"{file}"
            }
        },
        {
            "type": "text",
            "data": {
                "text": f"\n{'/'.join(music['level'])}"
            }
        }
    ])


@on_command('spec_rand', patterns="随个[绿黄红紫白]?[0-9]+\+?", only_to_me=False)
async def spec_random(session: CommandSession):
    level_labels = ['绿', '黄', '红', '紫', '白']
    regex = "随个([绿黄红紫白]?)([0-9]+\+?)"
    res = re.match(regex, session.current_arg)
    try:
        filted = []
        level = res.groups()[1]
        if res.groups()[0] == "":
            for music in music_data:
                try:
                    _ = music['level'].index(level)
                    filted.append(music)
                except Exception:
                    pass
        else:
            level_index = level_labels.index(res.groups()[0])
            for music in music_data:
                if level_index < len(music['level']):
                    if music['level'][level_index] == level:
                        filted.append(music)
        music = random_music(filted)
        await send_song(session, music)
    except Exception as e:
        print(e)
        await session.send("随机命令错误，请检查语法")


@on_command('mr', patterns=".*maimai.*什么", only_to_me=False)
async def natural_random(session: CommandSession):
    music = random_music(music_data)
    await send_song(session, music)
