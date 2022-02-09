from asyncio.windows_events import NULL
from nonebot import on_command, CommandSession
import requests
import urllib
from bs4 import BeautifulSoup
import re

URL = r"https://api.lolicon.app/setu/v2?"
HEADER = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"
}


@on_command(name='涩涩', patterns='不够[涩瑟色]|[涩瑟色]图|来一?[点份张].*[涩瑟色]图|再来[点份张]|看过了|铜')
async def _(session: CommandSession):
    keyword = session.current_arg[2:-2]
    tmp = re.sub('[Rr]18', '', keyword)
    r18 = 1
    if len(keyword) == len(tmp):
        r18 = 0
    else:
        keyword = tmp
    keyword = keyword.split('&amp;')
    # print(type(keyword))
    url = URL
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

    print(url)
    try:
        res = requests.get(url, timeout=5)
        js = res.json()
        pid = str(js['data'][0]['pid'])
        uid = str(js['data'][0]['uid'])
        author = str(js['data'][0]['author'])
        urlmsg = "https://pixiv.net/i/" + pid
    except:
        await session.send("没有找到这样的涩图QAQ")
        return

    ans = '作者：' + author + '\n链接：' + urlmsg
    await session.send(ans)

    # pic
    imgurl = js['data'][0]['urls']['original'].replace('cat', 're', 1)
    await session.send("[CQ:image,file=" + imgurl + ",cache=1]")
