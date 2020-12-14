from nonebot import on_command, CommandSession
import requests
import json
import random

music_data = requests.get("https://www.diving-fish.com/api/maimaidxprober/music_data").text
music_data = json.loads(music_data)


def random_music() -> dict:
    return music_data[random.randrange(0, len(music_data))]


@on_command('mr', patterns=".*maimai.*什么", only_to_me=False)
async def natural_random(session: CommandSession):
    music = random_music()
    if music['type'] == 'SD':
        t = '[标准]'
    else:
        t = '[DX]'
    await session.send(f"{t}{music['title']} {'/'.join(music['level'])}")
