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


def song_txt(music, file):
    return [
        {
            "type": "text",
            "data": {
                "text": f"{music['id']}. {music['title']}\n"
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
    ]


async def send_song(session: CommandSession, music: dict):
    file = f"https://www.diving-fish.com/covers/{music['id']}.jpg"
    await session.send(song_txt(music, file))


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


@on_command('search_music', patterns="查歌.+", only_to_me=False)
async def search_music(session: CommandSession):
    regex = "查歌(.+)"
    name = re.match(regex, session.current_arg).groups()[0].strip()
    if name == "":
        return
    res = []
    for music in music_data:
        try:
            music['title'].lower().index(name.lower())
            res.append(music)
        except ValueError:
            pass
    await session.send([
        {"type": "text",
            "data": {
                "text": f"{music['id']}. {music['title']}\n"
            }} for music in res])


@on_command('query_chart', patterns="[绿黄红紫白]?[dx|sd][0-9]+", only_to_me=False)
async def query_chart(session: CommandSession):
    regex = "([绿黄红紫白]?)((?:dx|sd)[0-9]+)"
    groups = re.match(regex, session.current_arg).groups()
    level_labels = ['绿', '黄', '红', '紫', '白']
    if groups[0] != "":
        try:
            level_index = level_labels.index(groups[0])
            level_name = ['Basic', 'Advanced', 'Expert', 'Master', 'Re: MASTER']
            name = groups[1]
            for music in music_data:
                if music['id'] == name:
                    break
            chart = music['charts'][level_index]
            ds = music['ds'][level_index]
            level = music['level'][level_index]
            file = f"https://www.diving-fish.com/covers/{music['id']}.jpg"
            if len(chart['notes']) == 4:
                msg = f'''{level_name[level_index]} {level}({ds})
TAP: {chart['notes'][0]}
HOLD: {chart['notes'][1]}
SLIDE: {chart['notes'][2]}
BREAK: {chart['notes'][3]}
谱师: {chart['charter']}
'''
            else:
                msg = f'''{level_name[level_index]} {level}({ds})
TAP: {chart['notes'][0]}
HOLD: {chart['notes'][1]}
SLIDE: {chart['notes'][2]}
TOUCH: {chart['notes'][3]}
BREAK: {chart['notes'][4]}
谱师: {chart['charter']}
'''
            await session.send([
                {
                    "type": "text",
                    "data": {
                        "text": f"{music['id']}. {music['title']}\n"
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
                        "text": msg
                    }
                }
            ])
        except Exception:
            await session.send("未找到该谱面")
    else:
        name = groups[1]
        for music in music_data:
            if music['id'] == name:
                break
        try:
            file = f"https://www.diving-fish.com/covers/{music['id']}.jpg"
            await session.send([
                {
                    "type": "text",
                    "data": {
                        "text": f"{music['id']}. {music['title']}\n"
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
                        "text": f"艺术家: {music['basic_info']['artist']}\n分类: {music['basic_info']['genre']}\nBPM: {music['basic_info']['bpm']}\n版本: {music['basic_info']['from']}\n难度: {'/'.join(music['level'])}"
                    }
                }
            ])
        except Exception:
            await session.send("未找到该乐曲")