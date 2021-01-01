import time

from aiocqhttp import Event
from nonebot import on_command, CommandSession, on_notice

help_text = """桜千雪です、よろしく。
可用命令如下：
.help 输出此消息
.jrrp 显示今天的人品值
.bind <角色名称> 绑定角色
.r/roll <掷骰表达式> 掷骰
.rc/rollcheck <技能/属性> [值] 技能/属性检定
.sc/sancheck <成功> <失败> 理智检定
.stat/st <技能/属性> <add|sub|set> <值> [触发时间（小时）] 增加/减少/设置属性值，可设定触发时间
.time <pass> [小时] 设置经过时间
.query/q <玩家名/QQ> <技能/属性> 查询某玩家的某属性
.intro/.i <玩家名> 查询此角色的基本信息
.showall/.sa 获取当前玩家的所有信息（将私聊发送）
.unbind 解绑角色
车卡网址：https://www.diving-fish.com/coc_card
要查看舞萌bot的有关帮助，请输入.help mai"""
mai_help_text = """桜千雪です、よろしく。
可用命令如下：
今日舞萌 查看今天的舞萌运势
XXXmaimaiXXX什么 随机一首歌
随个[dx/标准][绿黄红紫白]<难度> 随机一首指定条件的乐曲
[绿黄红紫白]<歌曲编号> 查询乐曲信息或谱面信息
<歌曲别名>是什么歌 查询乐曲别名对应的乐曲
定数查歌 <定数>  查询定数对应的乐曲
定数查歌 <定数下限> <定数上限>"""


@on_command('help', only_to_me=False)
async def help(session: CommandSession):
    v = session.current_arg_text.strip()
    if v == "":
        await session.send('''.help coc \t查看跑团相关功能
.help mai \t查看舞萌相关功能''')
    elif v == "mai":
        await session.send(mai_help_text)
    elif v == "coc":
        await session.send(help_text)


def hash(qq: int):
    days = int(time.strftime("%d", time.localtime(time.time()))) + 31 * int(
        time.strftime("%m", time.localtime(time.time()))) + 77
    return (days * qq) >> 8


@on_command('jrrp', only_to_me=False)
async def jrrp(session: CommandSession):
    qq = int(session.ctx['sender']['user_id'])
    h = hash(qq)
    rp = h % 100
    await session.send("【%s】今天的人品值为：%d" % (session.ctx['sender']['nickname'], rp))


@on_notice('notify.poke')
async def poke(event: Event):
    print(event)
