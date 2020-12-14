from nonebot import on_command, CommandSession
import requests
import json
import random
import re

music_data = requests.get("https://www.diving-fish.com/api/maimaidxprober/music_data").text
music_data = json.loads(music_data)


def random_music(data) -> dict:
    return data[random.randrange(0, len(music_data))]


@on_command('spec_rand', patterns="随个.?[0-9]+\+?", only_to_me=False)
async def spec_random(session: CommandSession):
    level_labels = ['绿', '黄', '红', '紫', '白']
    regex = "随个(.?)([0-9]+\+?)"
    res = re.match(regex, session.current_arg)
    try:
        level_index = level_labels.index(res.group()[1])
        level = level_labels.index(res.group()[2])
        filted = []
        for music in music_data:
            if level_index < len(music['level']):
                if music['level'][level_index] == level:
                    filted.append(music['level'])
        music = random_music(filted)
        if music['type'] == 'SD':
            t = '[标准]'
        else:
            t = '[DX]'
        await session.send(f"{t}{music['title']} {'/'.join(music['level'])}")
    except Exception:
        await session.send("随机命令错误，请检查语法")


@on_command('mr', patterns=".*maimai.*什么", only_to_me=False)
async def natural_random(session: CommandSession):
    music = random_music(music_data)
    if music['type'] == 'SD':
        t = '[标准]'
    else:
        t = '[DX]'
    await session.send(f"{t}{music['title']} {'/'.join(music['level'])}")
