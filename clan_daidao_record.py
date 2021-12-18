import hoshino
import re
from datetime import datetime
from hoshino import Service, priv
from hoshino.typing import *

sv = Service('clan_daidao_record')

status = dict() #{int:int}

xiashu_boss = 0
xiashu_time = ""

@sv.on_fullmatch('代刀帮助')
async def daidaoHelp(bot, ev: CQEvent):
    helpMessage = '''代刀模块指令列表：

上号@User  [记录上号 | 可@多个对象]
下号@User  [记录下号 | 可@多个对象 | 请在退出实战/登出账号后使用]

我的代刀  [查询自己的代刀状态]
所有代刀  [查询所有代刀状态]

清除代刀  [删除自己的代刀状态]
删除代刀@User  [删除指定刀手的所有代刀状态 | 仅@单个对象 | 需管理权限]
重置代刀  [删除所有代刀状态 | 需管理权限]

**新增**
下树[1-5] [通知所有人某Boss可以下树 | 需管理权限]
下树？    [查询最近的下树通知]
重置下树  [取消下树通知]
'''
    await bot.send(ev, helpMessage)

@sv.on_prefix('上号')
async def daidaoLogin(bot, ev: CQEvent):
    sender = int(ev.user_id)
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            uid = int(m.data['qq'])
            if uid in status:
                if status[uid] == sender:
                    msg = '您已经在此账号上'
                else:
                    at = str(MessageSegment.at(status[uid]))
                    msg = f'\n※※※※※请勿上号!※※※※※\n※※※※※请勿上号!※※※※※\n※※※※※请勿上号!※※※※※\n{at}正在代刀'
                await bot.send(ev, msg, at_sender = True)
            else:
                status[uid] = sender
                await bot.send(ev, "可以上号，已记录代刀", at_sender=True)

@sv.on_prefix('下号')
async def daidaoLogout(bot, ev: CQEvent):
    sender = int(ev.user_id)
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            uid = int(m.data['qq'])
            if not uid in status:
                await bot.send(ev, "该账号没有代刀", at_sender=True)
            elif sender != status[uid]:
                await bot.send(ev, "该账号不由您代刀", at_sender=True)
            else:
                del status[uid]
                await bot.send(ev, "已记录下号，请及时回到登录界面并删除登录记录，防止重开游戏自动登录原账号", at_sender=True)

@sv.on_fullmatch('我的代刀')
async def daidaoQuerySender(bot, ev: CQEvent):
    sender = int(ev.user_id)
    people = []
    
    for p in status:
        if status[p] == sender:
            people.append(p)
    
    if len(people) == 0:
        await bot.send(ev, "您当前没有代刀", at_sender = True)
    else:
        msg = "您负责的代刀："
        for p in people:
            at = str(MessageSegment.at(p))
            msg += f'\n{at}'
        await bot.send(ev, msg, at_sender = True)

@sv.on_fullmatch('所有代刀')
async def daidaoQueryAll(bot, ev: CQEvent):
    msgs = []
    for uid in status:
        at1= str(MessageSegment.at(status[uid]))
        at2= str(MessageSegment.at(uid))
        msg = f'{at1}代{at2}'
        msgs.append(msg)
    print(msgs)
    if len(msgs) == 0:
        await bot.send(ev, "当前没有代刀记录")
    else:
        step = 10
        temp = [msgs[i:i+step] for i in range(0, len(msgs), step)]
        for i in range(len(temp)):
            await bot.send(ev, '\n'.join(temp[i]))

@sv.on_fullmatch('清除代刀')
async def daidaoDelSender(bot, ev: CQEvent):
    sender = int(ev.user_id)
    to_be_del = []
    
    for p in status:
        if status[p] == sender:
            to_be_del.append(p)
    
    if len(to_be_del) == 0:
        await bot.send(ev, "您当前没有代刀")
    else:
        msg = "请确认所有账号均已登出（回到登录界面并删除登录记录）\n已清除代刀的账号："
        for p in to_be_del:
            del status[p]
            at = str(MessageSegment.at(p))
            msg += f'\n{at}'
        await bot.send(ev, msg, at_sender = True)

@sv.on_prefix('删除代刀')
async def daidaodelete(bot, ev: CQEvent):
    u_priv = priv.get_user_priv(ev)
    daoshou = []
    to_be_del = []
    
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            uid = int(m.data['qq'])
            daoshou.append(uid)
    
    if len(daoshou) != 1:
        await bot.send(ev, "请@一名刀手（仅一名）")
    elif u_priv < priv.ADMIN:
        await bot.send(ev, "权限不足")
    else:
        for p in status:
            if status[p] == daoshou[0]:
                to_be_del.append(p)
        
        if len(to_be_del) == 0:
            await bot.send(ev, "该刀手没有代刀")
        else:
            at = str(MessageSegment.at(daoshou[0]))
            msg = f'已删除{at}的代刀记录：'
            for p in to_be_del:
                del status[p]
                at = str(MessageSegment.at(p))
                msg += f'\n{at}'
            await bot.send(ev, msg)

@sv.on_fullmatch('重置代刀')
async def daidaoclear(bot, ev: CQEvent):
    u_priv = priv.get_user_priv(ev)
    if u_priv < priv.ADMIN:
        await bot.send(ev, "权限不足")
        return
    
    global status
    status = {}
    await bot.send(ev, "已重置代刀记录")

@sv.on_fullmatch('下树')
async def xiashuHelp(bot, ev: CQEvent):
    helpMessage = '''请按以下格式发送下树指令：
下树[1-5] [通知所有人某Boss可以下树 | 需管理权限]
下树？    [查询最近的下树通知]
重置下树  [取消下树通知]
'''
    await bot.send(ev, helpMessage)

@sv.on_fullmatch('下树1')
async def xiashu1(bot, ev: CQEvent):
    u_priv = priv.get_user_priv(ev)
    if u_priv < priv.ADMIN:
        await bot.send(ev, "权限不足")
        return
    
    global xiashu_boss
    xiashu_boss = 1
    global xiashu_time
    xiashu_time = datetime.now().strftime("%m/%d %I:%M%p")
    
    msg = '''************
**1王下树**
************'''
    await bot.send(ev, msg)

@sv.on_fullmatch('下树2')
async def xiashu2(bot, ev: CQEvent):
    u_priv = priv.get_user_priv(ev)
    if u_priv < priv.ADMIN:
        await bot.send(ev, "权限不足")
        return
    
    global xiashu_boss
    xiashu_boss = 2
    global xiashu_time
    xiashu_time = datetime.now().strftime("%m/%d %I:%M%p")
    
    msg = '''************
**2王下树**
************'''
    await bot.send(ev, msg)

@sv.on_fullmatch('下树3')
async def xiashu3(bot, ev: CQEvent):
    u_priv = priv.get_user_priv(ev)
    if u_priv < priv.ADMIN:
        await bot.send(ev, "权限不足")
        return
    
    global xiashu_boss
    xiashu_boss = 3
    global xiashu_time
    xiashu_time = datetime.now().strftime("%m/%d %I:%M%p")
    
    msg = '''************
**3王下树**
************'''
    await bot.send(ev, msg)

@sv.on_fullmatch('下树4')
async def xiashu4(bot, ev: CQEvent):
    u_priv = priv.get_user_priv(ev)
    if u_priv < priv.ADMIN:
        await bot.send(ev, "权限不足")
        return
    
    global xiashu_boss
    xiashu_boss = 4
    global xiashu_time
    xiashu_time = datetime.now().strftime("%m/%d %I:%M%p")
    
    msg = '''************
**4王下树**
************'''
    await bot.send(ev, msg)

@sv.on_fullmatch('下树5')
async def xiashu5(bot, ev: CQEvent):
    u_priv = priv.get_user_priv(ev)
    if u_priv < priv.ADMIN:
        await bot.send(ev, "权限不足")
        return
    
    global xiashu_boss
    xiashu_boss = 5
    global xiashu_time
    xiashu_time = datetime.now().strftime("%m/%d %I:%M%p")
    
    msg = '''************
**5王下树**
************'''
    await bot.send(ev, msg)

@sv.on_fullmatch('下树？')
@sv.on_fullmatch('下树?')
async def xiashuCheck(bot, ev: CQEvent):
    msg = ""
    
    if xiashu_boss == 0:
        msg = "无下树通知记录"
    else:
        msg = "最近的下树通知为：{}王\n通知时间：{}".format(xiashu_boss, xiashu_time)
    
    await bot.send(ev, msg)

@sv.on_fullmatch('重置下树')
async def xiashuClear(bot, ev: CQEvent):
    u_priv = priv.get_user_priv(ev)
    if u_priv < priv.ADMIN:
        await bot.send(ev, "权限不足")
        return
    
    global xiashu_boss
    xiashu_boss = 0
    global xiashu_time
    xiashu_time = ""
    
    await bot.send(ev, "下树通知/记录已清除")
