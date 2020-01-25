from nonebot import on_command, CommandSession, helpers
import requests
import demjson
import random
import math


class Event:
    def __init__(self, time, role_name, s1, s2, index, operation, value):
        self.time = time
        self.role_name = role_name
        self.s1 = s1
        self.s2 = s2
        self.index = index
        self.operation = operation
        self.value = value


class RollExpError(Exception):
    def __init__(self, msg):
        self.msg = msg


help_text = """桜千雪です、よろしく。
可用命令如下：
.help 输出此消息
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
车卡网址：https://www.diving-fish.com/coc_card"""
bg_text = """姓名：%s    玩家：%s
职业：%s    年龄：%s    性别：%s
住地：%s    出身：%s
形象描述：%s
思想与信念：%s
重要之人：%s
意义非凡之地：%s
宝贵之物：%s
特质：%s
伤口和疤痕：%s
恐惧症和狂躁症：%s
持有物品：%s"""
showall_text = """姓名：%s    玩家：%s
职业：%s    年龄：%s    性别：%s
住地：%s    出身：%s
技能/属性信息：
%s
形象描述：%s
思想与信念：%s
重要之人：%s
意义非凡之地：%s
宝贵之物：%s
特质：%s
伤口和疤痕：%s
恐惧症和狂躁症：%s
持有物品：%s"""
career_data = demjson.decode_file('career_data.json', encoding='utf-8')
role_cache = {}
time_event = []
binding_map = {}
stats_alias_map = {'力量': 'str', '体质': 'con', '体型': 'siz', '敏捷': 'dex', '外貌': 'app', '教育': 'edu', '智力': 'int',
                   '意志': 'pow', '体格': 'tg', '移动': 'mov', '生命': 'hp', '理智': 'san', '魔法': 'mp'}


def check_map(role):
    for key in binding_map:
        if binding_map[key] == role:
            return False
    return True


def flush_buffer(time):
    s = ""
    deletion = []
    for i in range(len(time_event)):
        event = time_event[i]
        event.time -= time
        if event.time <= 0:
            if event.index == -1:
                if event.operation == 0:
                    role_cache[event.role_name][event.s1][event.s2] = event.value
                    s += "【%s】的能力【%s】变成了【%d】！\n" % (event.role_name, event.s2, event.value)
                elif event.operation == 1:
                    role_cache[event.role_name][event.s1][event.s2] += event.value
                    s += "【%s】的能力【%s】上升了【%d】！\n" % (event.role_name, event.s2, event.value)
                elif event.operation == 2:
                    role_cache[event.role_name][event.s1][event.s2] -= event.value
                    s += "【%s】的能力【%s】下降了【%d】！\n" % (event.role_name, event.s2, event.value)
            else:
                skill = role_cache[event.role_name][event.s1][event.index]
                if event.operation == 0:
                    role_cache[event.role_name][event.s1][event.index][event.s2] = event.value
                    s += "【%s】的技能【%s】变成了【%d】！\n" % (event.role_name, skill['label'], event.value)
                elif event.operation == 1:
                    role_cache[event.role_name][event.s1][event.index][event.s2] += event.value
                    s += "【%s】的技能【%s】上升了【%d】！\n" % (event.role_name, skill['label'], event.value)
                elif event.operation == 2:
                    role_cache[event.role_name][event.s1][event.index][event.s2] -= event.value
                    s += "【%s】的技能【%s】下降了【%d】！\n" % (event.role_name, skill['label'], event.value)
            deletion.append(i)
    for i in deletion:
        del time_event[i]
    return s.strip()


def stat_modify(role, key: str, op: int, value: int, time=0):
    key = key.lower()
    try:
        key = stats_alias_map[key]
    except KeyError:
        pass
    try:
        r = role['stats'][key]
        event = Event(time, role['name'], 'stats', key, -1, op, value)
        time_event.append(event)
        return flush_buffer(0), True
    except KeyError:
        pass
    if len(key) <= 1:
        return "", False
    for skill in role['skills']:
        if key in skill['label']:
            index = role['skills'].index(skill)
            exp = "role_cache['%s']['skills'][%d]['sum']" % (role['name'], index)
            event = Event(time, role['name'], 'skills', 'sum', index, op, value)
            time_event.append(event)
            return flush_buffer(0), True
    return "", False


def search_check(role, key: str):
    key = key.lower()
    try:
        key = stats_alias_map[key]
    except KeyError:
        pass
    try:
        return role['stats'][key], True
    except KeyError:
        pass
    if len(key) <= 1:
        return "", False
    for skill in role['skills']:
        if key in skill['label']:
            return skill['sum'], True
    return "", False


def roll_term(rterm: str):
    arr = rterm.split('d')
    if len(arr) == 1:
        return "%d" % int(arr[0]), int(arr[0])
    elif len(arr) == 2:
        exp = ""
        total = 0
        for i in range(int(arr[0])):
            v = random.randint(1, int(arr[1]))
            exp += str(v) + "+"
            total += v
        return exp[:-1], total
    raise RollExpError


def roll_expression(rexp: str):
    rexp = rexp.lower()
    arr = rexp.split("+")
    exp = ""
    total = 0
    for elem in arr:
        s, i = roll_term(elem)
        exp += s + "+"
        total += i
    return "%s=%s=%d" % (rexp, exp[:-1], total), total


def gen_bg_text(role):
    career = career_data[role['career'] - 1]['label']
    gender = "女"
    items = ' '.join(role['item'])
    if role['gender'] == 1:
        gender = "男"
    t = (role['name'], role['player_name'], career, role['age'], gender, role['address'], role['from'],
        role['bg'][0], role['bg'][1], role['bg'][2], role['bg'][3], role['bg'][4], role['bg'][5], role['bg'][6], role['bg'][7], items)
    return bg_text % t


def gen_showall_text(role):
    career = career_data[role['career'] - 1]['label']
    gender = "女"
    items = ' '.join(role['item'])
    ability_str = ""
    for st in ['str', 'con', 'siz', 'dex', 'app', 'edu', 'int', 'pow', 'luck', 'hp', 'mp', 'mov', 'tg', 'san']:
        for st2 in stats_alias_map:
            if st == stats_alias_map[st2]:
                ability_str += "%s: %d\n" % (st2, role['stats'][st])
    ability_str += "\n"
    for sk in role['skills']:
        if sk['sum'] is None:
            sk['sum'] = 0
        ability_str += "%s: %d/%d/%d\n" % (sk['label'], sk['sum'], int(sk['sum'] / 2), int(sk['sum'] / 5))
    if role['gender'] == 1:
        gender = "男"
    t = (role['name'], role['player_name'], career, role['age'], gender, role['address'], role['from'], ability_str,
         role['bg'][0], role['bg'][1], role['bg'][2], role['bg'][3], role['bg'][4], role['bg'][5], role['bg'][6],
         role['bg'][7], items)
    return showall_text % t


def check(nickname, stat_name, value):
    rand = random.randint(1, 100)
    text = ""
    if rand <= value:
        if rand <= 3:
            text = "大成功"
        elif rand <= math.floor(value / 5):
            text = "极难成功"
        elif rand <= math.floor(value / 2):
            text = "困难成功"
        else:
            text = "成功"
    else:
        if rand > value:
            if rand >= 98:
                text = "大失败"
            else:
                text = "失败"
    return "【%s】进行【%s】检定: D100=%d/%d %s" % (nickname, stat_name, rand, value, text)


@on_command('help', aliases=['?'], only_to_me=False)
async def help(session: CommandSession):
    await session.send(help_text)


@on_command('unbind', only_to_me=False)
async def unbind(session: CommandSession):
    qq = session.ctx['sender']['user_id']
    try:
        var = binding_map[qq]
        del binding_map[qq]
        await session.send("解绑成功~")
    except KeyError:
        await session.send("你还未绑定角色哦~")


@on_command('intro', aliases=['i'], only_to_me=False)
async def intro(session: CommandSession):
    try:
        await session.send(gen_bg_text(role_cache[session.state['name']]))
    except KeyError:
        await session.send("未找到【%s】！这个角色似乎并没有出现在这个剧本里呢~" % session.state['name'])
        

@intro.args_parser
async def _(session: CommandSession):
    session.state['name'] = session.current_arg_text.strip()


@on_command('time', only_to_me=False)
async def time(session: CommandSession):
    t = session.state['time']
    s = flush_buffer(t)
    if s == "":
        await session.send("经过了%d小时，但没有玩家的能力值发生变化。" % t)
    else:
        await session.send("经过%d小时后，玩家的能力发生了如下变化：\n%s" % (t, s))


@time.args_parser
async def _(session: CommandSession):
    session.state['time'] = int(session.current_arg_text.strip().split(' ')[-1])


@on_command('stat', aliases=['st'], only_to_me=False)
async def stat(session: CommandSession):
    argc = session.state['argc']
    argv = session.state['argv']
    if session.state['error']:
        await session.send("你这白痴又弄错命令格式了！给我记好了，正确的格式是.stat <技能/属性> <add|sub|set> <值> [触发时间（小时）]！")
        return
    role = None
    try:
        role = role_cache[binding_map[session.ctx['sender']['user_id']]]
    except KeyError:
        await session.send("【%s】看起来还没绑定角色呢。输入.bind <角色名称> 进行绑定吧？" % (session.ctx['sender']['nickname']))
        return
    if argc == 1:
        stat_name = argv[0]
        value, err = search_check(role, stat_name)
        if not err:
            await session.send("未找到能力值【%s】！真的有这个能力吗？" % stat_name)
            return
        await session.send("【%s】的能力值【%s】为：%d/%d/%d" % (role['name'], stat_name, value, int(value / 2), int(value / 5)))
        return
    elif argc >= 3:
        time = 0
        if argc == 4:
            time = int(argv[3])
        m = {'add': 1, 'sub': 2, 'set': 0}
        try:
            op = m[argv[1]]
        except KeyError:
            await session.send("看起来命令不支持【%s】这个操作呢~" % argv[1])
            return
        s, e = stat_modify(role, argv[0], op, int(argv[2]), time)
        if not e:
            await session.send("未找到能力值【%s】！真的有这个能力吗？" % argv[0])
        else:
            if time == 0:
                await session.send(s)
            else:
                await session.send("【%s】的【%s】会在%d小时后发生变化~" % (role['name'], argv[0], time))


@stat.args_parser
async def _(session: CommandSession):
    session.state['error'] = False
    text = session.current_arg_text.strip()
    arr = text.split(' ')
    session.state['argc'] = len(arr)
    if len(arr) != 1 and len(arr) != 3 and len(arr) != 4:
        session.state['error'] = True
        return
    session.state['argv'] = arr


@on_command('showall', aliases=['sa'], only_to_me=False)
async def showall(session: CommandSession):
    qq = session.ctx['sender']['user_id']
    try:
        nickname = binding_map[qq]
        role = role_cache[nickname]
        await session.send(gen_showall_text(role), ensure_private=True)
        await session.send("已发送私聊消息~", at_sender=True)
    except KeyError:
        await session.send("【%s】看起来还没绑定角色呢。输入.bind <角色名称> 进行绑定吧？" % (session.ctx['sender']['nickname']))
        return


@on_command('query', aliases=['q'], only_to_me=False)
async def query(session: CommandSession):
    if session.state['error']:
        await session.send("你这白痴又弄错命令格式了！给我记好了，正确的格式是.q <玩家名/QQ> <技能/属性>！")
        return
    role = None
    try:
        role = role_cache[binding_map[int(session.state['user'])]]
    except Exception:
        try:
            role = role_cache[session.state['user']]
        except Exception:
            await session.send("未找到【%s】！这个角色似乎并没有出现在这个剧本里呢~" % session.state['user'])
            return
    stat_name = session.state['stat']
    value, err = search_check(role, stat_name)
    if not err:
        await session.send("未找到能力值【%s】！真的有这个能力吗？" % stat_name)
        return
    await session.send("【%s】的能力值【%s】为：%d/%d/%d" % (role['name'], stat_name, value, int(value / 2), int(value / 5)))
        

@query.args_parser
async def _(session: CommandSession):
    session.state['error'] = False
    text = session.current_arg_text.strip()
    arr = text.split(' ')
    if len(arr) != 2:
        session.state['error'] = True
        return
    session.state['user'] = arr[0]
    session.state['stat'] = arr[1]


@on_command('roll', aliases=['r'], only_to_me=False)
async def roll(session: CommandSession):
    result = roll_expression(session.state['exp'])
    name = session.ctx['sender']['nickname']
    try:
        name = binding_map[session.ctx['sender']['user_id']]
    except KeyError:
        pass
    await session.send("【%s】的掷骰结果：%s" % (name, result[0]))


@roll.args_parser
async def _(session: CommandSession):
    session.state['exp'] = session.current_arg_text.strip()


@on_command('sancheck', aliases=['sc'], only_to_me=False)
async def sancheck(session: CommandSession):
    qq = session.ctx['sender']['user_id']
    try:
        nickname = binding_map[qq]
        if session.state['error']:
            await session.send("你这白痴又弄错命令格式了！给我记好了，正确的格式是.sc <成功> <失败>！")
            return
        role = role_cache[nickname]
        value = random.randint(1, 100)
        sanity = role['stats']['san']
        print(roll_expression(session.state['expression_f']))
        if value > sanity:
            s, v = roll_expression(session.state['expression_f'])
            role['stats']['san'] -= v
            await session.send("【%s】的理智检定：%d/%d 失败，理智扣除%s点，剩余%d点" % (nickname, value, sanity, s, role['stats']['san']))
        else:
            s, v = roll_expression(session.state['expression_s'])
            role['stats']['san'] -= v
            await session.send("【%s】的理智检定：%d/%d 成功，理智扣除%s点，剩余%d点" % (nickname, value, sanity, s, role['stats']['san']))
    except KeyError:
        await session.send("【%s】看起来还没绑定角色呢。输入.bind <角色名称> 进行绑定吧？" % (session.ctx['sender']['nickname']))
        return


@sancheck.args_parser
async def _(session: CommandSession):
    session.state['error'] = False
    text = session.current_arg_text.strip()
    arr = text.split(' ')
    if len(arr) != 2:
        session.state['error'] = True
        return
    session.state['expression_s'] = arr[0]
    session.state['expression_f'] = arr[1]


@on_command('rollcheck', aliases=['rc'], only_to_me=False)
async def rollcheck(session: CommandSession):
    qq = session.ctx['sender']['user_id']
    nickname = binding_map[qq]
    if session.state['error']:
        await session.send("你这白痴又弄错命令格式了！给我记好了，正确的格式是.rc <技能/属性> [值]！")
        return
    stat_name = session.state['stat_name']
    if session.state['diy']:
        value = session.state['value']
        await session.send(check(nickname, stat_name, value))
        return
    try:
        role = role_cache[nickname]
        value, err = search_check(role, stat_name)
        if not err:
            await session.send("未找到能力值【%s】！真的有这个能力吗？" % stat_name)
            return
        await session.send(check(nickname, stat_name, value))
    except KeyError:
        await session.send("【%s】看起来还没绑定角色呢。输入.bind <角色名称> 进行绑定吧？" % (session.ctx['sender']['nickname']))
        return


@rollcheck.args_parser
async def _(session: CommandSession):
    session.state['error'] = False
    text = session.current_arg_text.strip()
    arr = text.split(' ')
    if len(arr) == 1:
        session.state['diy'] = False
        session.state['stat_name'] = arr[0]
    elif len(arr) == 2:
        session.state['diy'] = True
        session.state['stat_name'] = arr[0]
        try:
            session.state['value'] = int(arr[1])
        except Exception:
            session.state['error'] = True
    else:
        session.state['error'] = True


@on_command('bind', only_to_me=False)
async def bind(session: CommandSession):
    name = session.get("name")
    qq = session.ctx['sender']['user_id']
    try:
        var = binding_map[qq]
    except KeyError:
        try:
            var = role_cache[name]
        except KeyError:
            text = requests.get("https://www.diving-fish.com:25565/query", {"name": name}).text
            if text == "{}":
                await session.send("千雪没能找到角色【%s】，下次再出错就把你拉入黑名单了哦！" % name)
                return
            role_cache[name] = demjson.decode(text, encoding='utf-8')
        if check_map(name):
            binding_map[qq] = name
        else:
            await session.send("这个角色已经绑定过啦！难道还想两个人控制一个角色吗？！")
            return
        await session.send("绑定成功！现在千雪已经认为【%s】就是【%s】了哦！" % (session.ctx['sender']['nickname'], name))
        return
    await session.send("你已经绑定过角色了哟~")


@bind.args_parser
async def _(session: CommandSession):
    session.state['name'] = session.current_arg_text.strip()