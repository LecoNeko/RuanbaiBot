from time import sleep
from nonebot import on_command, CommandSession, MessageSegment
from plugins.utils import *
from config import WHITEGROUPLIST

SETUAPI = r"https://api.lolicon.app/setu/v2?"
HEADER = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"
}

@on_command(name='涩涩', patterns='不够[涩瑟色]|[涩瑟色]图|来一?[点份张].*[涩瑟色]图|再来[点份张]|看过了|铜')
async def _(session: CommandSession):
    print(session.event)
    if session.event['message_type'] == 'group':
        if session.event.group_id not in WHITEGROUPLIST:
            await session.send('SETU只在允许的群内发送QAQ')
            return

    ans = getSetuInfo(session.current_arg_text.strip())
    if not ans:
        await session.send("没有找到涩图QAQ")
        return
    await session.send(ans[0])
    setu = setuMesg(ans[1])
    await session.send(setu)
    #if session.event['message_type'] == 'group':
    #    print('\n\n\n\n\n')
    #    sleep(5)
    #    session.bot.delete_msg(message_id = session.event['message_id'], self_id = session.self_id)



