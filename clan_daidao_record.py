import hoshino
from hoshino import Service, priv
from hoshino.typing import *
from datetime import datetime, timedelta
from . import status

sv = Service('clan_daidao_record')

@sv.on_fullmatch('代刀帮助')
async def daidaoHelp(bot, ev: CQEvent):
    helpMessage = '''代刀模块指令列表：

上号@User  [记录上号 | 可@多个对象]
下号@User  [记录下号 | 可@多个对象 | 请在退出实战/登出账号后使用]

我的代刀  [查询自己的代刀状态]
所有代刀  [查询所有代刀状态]

清除代刀  [删除自己的代刀状态]
删除代刀@User  [删除指定刀手的所有代刀状态 | 仅@单个对象 | 需要管理权限]
重置代刀  [删除所有代刀状态 | 需要管理权限]

**新增**
代刀次数(@User): yy-mm-dd: h+d [查询指定用户（不指定则为自己）在指定时间段内的代刀次数 | 可@多个对象 | 例：代刀次数: 22-3-1: 18+4 （3月1日晚上6点到10点 自己的代刀次数）]
删除历史: yy-mm-dd [删除指定日期之前的所有历史记录 | 需要管理权限]

--移除--
下树通知
'''
    await bot.send(ev, helpMessage)

@sv.on_prefix('上号')
async def daidaoLogin(bot, ev: CQEvent):
    con = status.connect(str(ev.group_id))
    sender = str(ev.user_id)
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            uid = str(m.data['qq'])
            curLoggedin = status.loginStatus(con, uid)
            if curLoggedin is not None:
                if curLoggedin == sender:
                    msg = '您已经在此账号上'
                else:
                    at = str(MessageSegment.at(curLoggedin))
                    msg = '\n※※※※※请勿上号!※※※※※\n※※※※※请勿上号!※※※※※\n※※※※※请勿上号!※※※※※\n{}正在代刀'.format(at)
                await bot.send(ev, msg, at_sender = True)
            else:
                status.login(con, sender, uid)
                await bot.send(ev, '可以上号，已记录代刀', at_sender=True)
    con.close()

@sv.on_prefix('下号')
async def daidaoLogout(bot, ev: CQEvent):
    con = status.connect(str(ev.group_id))
    sender = str(ev.user_id)
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            uid = str(m.data['qq'])
            curLoggedin = status.loginStatus(con, uid)
            if curLoggedin is None:
                await bot.send(ev, '该账号没有代刀', at_sender=True)
            elif curLoggedin != sender:
                await bot.send(ev, '该账号不由您代刀', at_sender=True)
            else:
                status.logout(con, uid)
                await bot.send(ev, '已记录下号，请及时回到登录界面并删除登录记录，防止重开游戏自动登录原账号', at_sender=True)
    con.close()

@sv.on_fullmatch('我的代刀')
async def daidaoQuerySender(bot, ev: CQEvent):
    con = status.connect(str(ev.group_id))
    sender = str(ev.user_id)
    records = status.getCurStatus(con, sender)
    con.close()
    
    if records == []:
        await bot.send(ev, '您当前没有代刀', at_sender = True)
    else:
        msg = "您负责的代刀："
        for _, p in records:
            at = str(MessageSegment.at(p))
            msg += '\n{}'.format(at)
        await bot.send(ev, msg, at_sender = True)

@sv.on_fullmatch('所有代刀')
async def daidaoQueryAll(bot, ev: CQEvent):
    con = status.connect(str(ev.group_id))
    msgs = []
    for u1, u2 in status.getCurStatus(con):
        at1= str(MessageSegment.at(u1))
        at2= str(MessageSegment.at(u2))
        msg = '{}代{}'.format(at1, at2)
        msgs.append(msg)
    con.close()
    #print(msgs)
    if msgs == []:
        await bot.send(ev, '当前没有代刀记录')
    else:
        step = 10
        temp = [msgs[i:i+step] for i in range(0, len(msgs), step)]
        for i in range(len(temp)):
            await bot.send(ev, '\n'.join(temp[i]))

@sv.on_fullmatch('清除代刀')
async def daidaoDelSender(bot, ev: CQEvent):
    con = status.connect(str(ev.group_id))
    sender = str(ev.user_id)
    
    records = status.getCurStatus(con, sender)
    if records == []:
        await bot.send(ev, '您当前没有代刀')
    else:
        status.logoutAll(con, sender)
        msg = '请确认所有账号均已登出（回到登录界面并删除登录记录）\n已清除代刀的账号：'
        for _, p in records:
            at = str(MessageSegment.at(p))
            msg += '\n{}'.format(at)
        await bot.send(ev, msg, at_sender = True)
    con.close()

@sv.on_prefix('删除代刀')
async def daidaodelete(bot, ev: CQEvent):
    u_priv = priv.get_user_priv(ev)
    con = status.connect(str(ev.group_id))
    daoshou = []
    records = []
    
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            uid = str(m.data['qq'])
            daoshou.append(uid)
    
    if len(daoshou) != 1:
        await bot.send(ev, '请@一名刀手（仅一名）')
    elif u_priv < priv.ADMIN:
        await bot.send(ev, '权限不足')
    else:
        records = status.getCurStatus(con, daoshou[0])
        
        if records == []:
            await bot.send(ev, '该刀手没有代刀')
        else:
            status.logoutAll(con, daoshou[0])
            at = str(MessageSegment.at(daoshou[0]))
            msg = '已删除{}的代刀记录：'.format(at)
            for _, p in records:
                at = str(MessageSegment.at(p))
                msg += '\n{}'.format(at)
            await bot.send(ev, msg)
    con.close()

@sv.on_fullmatch('重置代刀')
async def daidaoclear(bot, ev: CQEvent):
    u_priv = priv.get_user_priv(ev)
    if u_priv < priv.ADMIN:
        await bot.send(ev, '权限不足')
        return
    
    con = status.connect(str(ev.group_id))
    status.clearStatus(con)
    con.close()
    await bot.send(ev, '已重置代刀记录')

@sv.on_prefix('代刀次数')
async def daidaoCount(bot, ev: CQEvent):
    request = ev.raw_message.split(']')[-1].replace('：', ':').replace(' ', '').split(':')[1:]
    if len(request) != 2:
        await bot.send(ev, '请按照正确格式发送请求\n代刀次数(@User): yy-mm-dd: h+d')
        return None
    
    try:
        hours = request[1].split('+')
        dt1 = datetime.strptime('{}-{}'.format(request[0], hours[0]), '%y-%m-%d-%H')
        dt2 = dt1 + timedelta(hours = int(hours[1]))
        t1 = dt1.strftime('%y-%m-%d %H:%M')
        t2 = dt2.strftime('%y-%m-%d %H:%M')
    except:
        await bot.send(ev, '请按照正确格式发送请求\n代刀次数(@User): yy-mm-dd: h+d')
        return None
    
    con = status.connect(str(ev.group_id))
    checkSelf = True
    
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            checkSelf = False
            uid = str(m.data['qq'])
            count = status.getDaidaoCount(con, uid, dt1, dt2)
            at = str(MessageSegment.at(uid))
            msg = '{}在{}到{}之间的上号次数为：{}次'.format(at, t1, t2, count)
            await bot.send(ev, msg)
    
    if checkSelf:
        uid = str(ev.user_id)
        count = status.getDaidaoCount(con, uid, dt1, dt2)
        at = str(MessageSegment.at(uid))
        msg = '{}在{}到{}之间的上号次数为：{}次'.format(at, t1, t2, count)
        await bot.send(ev, msg)
    
    con.close()

@sv.on_prefix('删除历史')
async def clearHistory(bot, ev: CQEvent):
    u_priv = priv.get_user_priv(ev)
    if u_priv < priv.ADMIN:
        await bot.send(ev, '权限不足')
        return
    
    request = ev.raw_message.replace('：', ':').replace(' ', '').split(':')
    if len(request) != 2:
        await bot.send(ev, '请按照正确格式发送请求\n删除历史: yy-mm-dd')
        return None
    
    try:
        dt = datetime.strptime(request[1], '%y-%m-%d')
        t = dt.strftime('%y-%m-%d')
    except:
        await bot.send(ev, '请按照正确格式发送请求\n删除历史: yy-mm-dd')
        return None
    
    con = status.connect(str(ev.group_id))
    status.deleteHistory(con, dt)
    con.close()
    
    msg = '已删除直到{}为止的代刀记录'.format(t)
    await bot.send(ev, msg)
