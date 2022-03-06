import asyncio
from nonebot import on_command, CommandSession
import random
import time

from sqlalchemy import false
from plugins.utils import *

getLimit = {'time': time.time(), 'cnt':0}

def timeChecker():
    if getLimit['time']-time.time() > 60:
        getLimit['time'] = time.time()
        getLimit['cnt'] = 0
    if getLimit['cnt'] > 35:
        return False
    getLimit['cnt'] += 1
    return True

def check_num(s:str):
    for i in s:
        if not i.isdigit():
            return False
    return True


@on_command(name='o', patterns=gene_Aa_ReStr('osu'), privileged = True)
async def _(session: CommandSession):
    if timeChecker() == False:
        await session.send('请求过于频繁！请稍后再试试吧~')
        return
    cur_text = session.current_arg_text.strip().split()
    Method = cur_text[0]
    if re.fullmatch(gene_Aa_ReStr('info'), Method):
        if len(cur_text) < 2:
            return
        mode = str(3)
        if check_num(cur_text[-1]):
            mode = cur_text[-1]
            cur_text = cur_text[:-1]
        User = cur_text[1]
        for i in cur_text[2:]:
            User += ' ' + i
        Info = await OsuInfo(User, mode)
        if not Info or Info == '网络错误':
            await session.send(Info)
        await session.send(Info)
    if re.fullmatch(gene_Aa_ReStr('re'), Method):
        getLimit['cnt'] += 1
        if len(cur_text) < 2:
            return
        mode = str(3)
        if check_num(cur_text[-1]):
            mode = cur_text[-1]
            cur_text = cur_text[:-1]
        User = cur_text[1]
        for i in cur_text[2:]:
            User += ' ' + i
        Info = await OsuRe(User, mode)
        if not Info or Info == '网络错误':
            await session.send(Info)
        await session.send(Info)
