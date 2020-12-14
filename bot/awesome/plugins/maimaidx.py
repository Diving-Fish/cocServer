from nonebot import on_command, CommandSession
import requests
import demjson
import random

music_data = requests.get("https://www.diving-fish.com/api/maimaidxprober/music_data").text
music_data = demjson.decode(music_data, encoding='utf-8')


def random_music() -> dict:
    return music_data[random.randrange(0, len(music_data))]


@on_command('mr', patterns=".*maimai.*什么", only_to_me=False)
def natural_random(session: CommandSession):
    music = random_music()
    if music['type'] == 'SD':
        t = '[标准]'
    else:
        t = '[DX]'
    await session.send(f"{t}{music['title']} {'/', music['level']}")
