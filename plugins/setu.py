import asyncio
import time
from nonebot import on_command, CommandSession
import random
from plugins.utils import *
from config import HDELETET_TIME, WHITEGROUPLIST, BLACKLIST, DELETE_TIME

SETUAPI = r"https://api.lolicon.app/setu/v2?"
HEADER = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"
}

setulimit = {}

clear_time = [0]

async def setuDelete(session, setu_message_id, R18):
    if R18 == 0:
        await asyncio.sleep(DELETE_TIME)
    else:
        await asyncio.sleep(HDELETET_TIME)
    await session.bot.delete_msg(
        message_id=int(setu_message_id['message_id']))
    deletelist.remove(setu_message_id['message_id'])


def makeLimit(user_id: int):
    user_id = str(user_id)
    nowtime = time.time()
    if nowtime - clear_time[0] > 3600 * 6:
        setulimit.clear()
        clear_time[0] = nowtime

    if user_id not in setulimit:
        setulimit[user_id] = [0, 0]
    lasttime, count = setulimit.get(user_id, [0, 0])
    dis = (nowtime - lasttime) / float(60 * 60)
    if dis < 1.0:
        if count >= 15:
            return count
    else:
        setulimit[user_id] = [nowtime, 0]
    return 0


numHZ = {'一' : 1 ,'二' : 2, '三' : 3, '四' : 4, '五' : 5, '六' : 6, '七' : 7, '八' : 8, '九' : 9}


on_running = [0]
deletelist = []

@on_command(name='涩涩', patterns='不够[涩瑟色]|[涩瑟色]图|来一?[点份张].*[涩瑟色]图|再来[点份张]|看过了|炼铜|重工业', privileged=True)
async def _(session: CommandSession):
    # print(session.event)
    # if session.event['message_type'] == 'group' and session.event.group_id not in WHITEGROUPLIST\
    #    or session.event['message_type'] == 'private' and session.event.sender_id in BLACKLIST:
    #        await session.send('SETU只在允许的群内发送QAQ')
    #        return
    if len(deletelist) > 0:
        for id in deletelist:
            try:
                asyncio.gather(session.bot.delete_msg(message_id=int(id)))
            except:
                pass
        deletelist.clear()
    if on_running[0] > 3:
        await session.send("涩涩太频繁惹！请过一会再试试吧~")
        return
    on_running[0] += 1

    R18 = 1
    cnt = 1
    keyword = session.current_arg_text.strip()
    sese = makeLimit(session.event['sender']['user_id'])
    if session.event['message_type'] == 'group':
        if session.event.group_id not in WHITEGROUPLIST:
            if len(re.findall('[Rr]18',keyword)) > 0:
                await session.send('不可以涩涩！！！')
                return

            R18 = 0
            if sese >= 15:
                await session.send("最近已经涩涩过{}次惹，请休息一会~".format(sese))
                return
    else:
        if sese >= 15:
            await session.send("最近已经涩涩过{}次惹，请休息一会~".format(sese))
            return

    tmp = re.findall('来.*张', keyword) 
    if len(tmp):
        tmp = tmp[0][1:-1]
        if tmp in numHZ:
            cnt = numHZ[tmp]
        else:
            try:
                cnt = int(tmp)
            except:
                cnt = 1
        ed = 1
        while keyword[ed] != '张':
            ed += 1
        keyword = keyword[0:1] + keyword[ed:]
        cnt = min(5, max(1, cnt))
    
    setulimit[str(session.event['sender']['user_id'])][1] += cnt

    first_in = True
    while cnt > 0:
        ans = await getSetuInfo(keyword, R18)
        if not ans:
            if first_in == True:
                await session.send("没有找到涩图QAQ")
                return
            continue

        first_in = False
        await session.send(ans[0], at_sender=True)
        setu = setuMesg(ans[1])
        R18 = ans[2]
        setu_message_id = await session.send(setu)

        # 仅撤回群组涩图
        if session.event['message_type'] == 'group' and setu_message_id:
            deletelist.append(setu_message_id)
            asyncio.gather(setuDelete(session, setu_message_id, R18))

        cnt -= 1
    on_running[0] -= 1


@on_command(name='drogonpic', patterns='来一?[点份张][龍龙龍]图', privileged=True)
async def _(session: CommandSession):
    path = os.path.join(os.path.dirname(__file__), 'pic_src', 'drogon')
    filenames = os.listdir(path)
    file = os.path.join(path, filenames[random.randint(0, len(filenames)-1)])
    img = MessageLocalImage(file)
    await session.send(img)

async def getSetuInfo(keyword: str, R18flag: int):
    '''
    从消息中提取涩图tag并获取涩图的info
    '''
    #print('\n')
    #print(keyword)
    r18 = R18flag
    if keyword=='炼铜' or keyword=='重工业':
        tmp = re.sub('[Rr]18', '', keyword)
        url = SETUAPI + 'tag=萝莉|幼女'
        r18 = 0
    else:
        keyword = keyword[2:-2]
        tmp = re.sub('[Rr]18', '', keyword)
        if len(keyword) == len(tmp):
            r18 = 0
        else:
            keyword = tmp
        keyword = keyword.split('&amp;')
        # print(type(keyword))
        url = SETUAPI
        url = url + 'r18=' + str(r18) + '&'
        last = 0
        for iter in keyword:
            if not last:
                last = 1
            else:
                url = url + '&'
            url =url + "tag="
            item = iter.split('|')
            first = 1
            for i in item:
                if not first:
                    url = url + '|'
                url = url + i
                first = 0
    #print(url)
    try:
        res = await async_request(url=url)
        js = res.json()
        pid = str(js['data'][0]['pid'])
        uid = str(js['data'][0]['uid'])
        author = str(js['data'][0]['author'])
        urlmsg = "https://pixiv.net/i/" + pid
    except:
        return None
    ans = '作者：' + author + '\n链接：' + urlmsg

    return [ans, js['data'][0]['urls']['original'].replace('cat', 're', 1), r18]

