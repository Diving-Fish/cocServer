from collections import defaultdict

from nonebot import on_command, CommandSession, argparse
import requests
import json
import random
import re
from awesome.plugins.public import hash
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


def inner_level_q(ds1, ds2=None):
    result_set = []
    diff_label = ['Bas', 'Adv', 'Exp', 'Mst', 'REM']
    for music in music_data:
        for i in range(len(music['ds'])):
            if ds2 is None:
                if music['ds'][i] == ds1:
                    result_set.append((music['id'], music['title'], music['ds'][i], diff_label[i], music['level'][i]))
            elif ds1 <= music['ds'][i] <= ds2:
                result_set.append((music['id'], music['title'], music['ds'][i], diff_label[i], music['level'][i]))
    return result_set


@on_command('inner_level', aliases=['定数查歌'], only_to_me=False, shell_like=True)
async def inner_level_query(session: CommandSession):
    argv = session.args['argv']
    if len(argv) > 2 or len(argv) == 0:
        await session.send("命令格式为\n定数查歌 <定数>\n定数查歌 <定数下限> <定数上限>")
        return
    if len(argv) == 1:
        result_set = inner_level_q(float(argv[0]))
    else:
        result_set = inner_level_q(float(argv[0]), float(argv[1]))
    if len(result_set) > 50:
        await session.send("数据超出 50 条，请尝试缩小查询范围")
        return
    s = ""
    for elem in result_set:
        s += f"{elem[0]}. {elem[1]} {elem[3]} {elem[4]}({elem[2]})\n"
    await session.send(s.strip())


@on_command('spec_rand', patterns="随个(?:dx|sd|标准)?[绿黄红紫白]?[0-9]+\+?", only_to_me=False)
async def spec_random(session: CommandSession):
    level_labels = ['绿', '黄', '红', '紫', '白']
    regex = "随个((?:dx|sd|标准))?([绿黄红紫白]?)([0-9]+\+?)"
    res = re.match(regex, session.current_arg.lower())
    try:
        filted = []
        if res.groups()[0] == "dx":
            tp = ["DX"]
        elif res.groups()[0] == "sd" or res.groups()[0] == "标准":
            tp = ["SD"]
        else:
            tp = ["SD", "DX"]
        level = res.groups()[2]
        if res.groups()[1] == "":
            for music in music_data:
                if music['type'] not in tp:
                    continue
                try:
                    _ = music['level'].index(level)
                    filted.append(music)
                except Exception:
                    pass
        else:
            level_index = level_labels.index(res.groups()[1])
            for music in music_data:
                if level_index < len(music['level']):
                    if music['level'][level_index] == level and music['type'] in tp:
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
    if res == []:
        await session.send("未找到此乐曲")
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


wm_list = ['拼机', '推分', '越级', '下埋', '夜勤', '练底力', '练手法', '打旧框', '干饭', '抓绝赞', '收歌']


@on_command('今日舞萌', aliases=['今日mai'], only_to_me=False)
async def jrwm(session: CommandSession):
    qq = int(session.ctx['sender']['user_id'])
    h = hash(qq)
    rp = h % 100
    wm_value = []
    for i in range(11):
        wm_value.append(h & 3)
        h >>= 2
    s = f"今日人品值：{rp}\n"
    for i in range(11):
        if wm_value[i] == 3:
            s += f'宜 {wm_list[i]}\n'
        elif wm_value[i] == 0:
            s += f'忌 {wm_list[i]}\n'
    s += "千雪提醒您：打机时不要大力拍打或滑动哦\n今日推荐歌曲："
    music = music_data[h % len(music_data)]
    await session.send([
        {"type": "text", "data": {"text": s}}
    ] + song_txt(music, f"https://www.diving-fish.com/covers/{music['id']}.jpg"))


music_aliases = defaultdict(list)
f = open('./aliases.csv', 'r', encoding='utf-8')
tmp = f.readlines()
f.close()
for t in tmp:
    arr = t.strip().split('\t')
    for i in range(len(arr)):
        if arr[i] != "":
            music_aliases[arr[i].lower()].append(arr[0])


@on_command('find_song', patterns=".+是什么歌", only_to_me=False)
async def find_song(session: CommandSession):
    regex = "(.+)是什么歌"
    name = re.match(regex, session.current_arg).groups()[0].strip().lower()
    if name not in music_aliases:
        await session.send("未找到此歌曲\n舞萌 DX 歌曲别名收集计划：https://docs.qq.com/sheet/DQ0pvUHh6b1hjcGpl")
        return
    result_set = music_aliases[name]
    if len(result_set) == 1:
        for music in music_data:
            if music['title'] == result_set[0]:
                break
        await session.send([{"type": "text", "data": {"text": "您要找的是不是"}}] + song_txt(music, f"https://www.diving-fish.com/covers/{music['id']}.jpg"))
    else:
        s = '\n'.join(result_set)
        await session.send(f"您要找的可能是以下歌曲中的其中一首：\n{ s }")