import asyncio
from nonebot import on_command, CommandSession
from plugins.utils import *
from config import HDELETET_TIME, WHITEGROUPLIST, BLACKLIST, DELETE_TIME

SETUAPI = r"https://api.lolicon.app/setu/v2?"
HEADER = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"
}

@on_command(name='涩涩', patterns='不够[涩瑟色]|[涩瑟色]图|来一?[点份张].*[涩瑟色]图|再来[点份张]|看过了|炼铜|重工业', privileged = True)
async def _(session: CommandSession):
    #print(session.event)
    #if session.event['message_type'] == 'group' and session.event.group_id not in WHITEGROUPLIST\
    #    or session.event['message_type'] == 'private' and session.event.sender_id in BLACKLIST:
    #        await session.send('SETU只在允许的群内发送QAQ')
    #        return
    
    R18 = 1
    if session.event['message_type'] == 'group':
        if session.event.group_id in WHITEGROUPLIST:
            R18 = 1
        else:
            R18 = 0

    keyword = session.current_arg_text.strip()

    tmp = re.findall('来.*张',keyword)
    if len(tmp):
        tmp = tmp[0][1:-1]
        try:
            cnt = int(tmp)
        except:
            cnt = 1
        ed = 1
        while keyword[ed]!='张':
            ed+=1
        keyword = keyword[0:1] + keyword[ed:]
        cnt = min(5, max(1, cnt))
    first_in = True
    while cnt > 0:
        ans = await getSetuInfo(keyword, R18)
        if not ans:
            if first_in == True: 
                await session.send("没有找到涩图QAQ")
                return
            continue
        first_in = False
        #print(setulist)
        #print('\n\n\n')
        await session.send(ans[0], at_sender = True)
        setu = setuMesg(ans[1])
        R18 = ans[2]
        setu_message_id = await session.send(setu)
        
        # 仅撤回群组涩图
        if session.event['message_type'] == 'group' and setu_message_id:
            #print('\n\n\n\n\n')
            if R18 == 0:
                await asyncio.sleep(DELETE_TIME)
            else:
                await asyncio.sleep(HDELETET_TIME)
            await session.bot.delete_msg(
                message_id = int(setu_message_id['message_id']))
        cnt -= 1



