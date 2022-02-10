from tokenize import String
from nonebot import on_command, CommandSession, MessageSegment
import requests
from bs4 import BeautifulSoup
import re

URL = r"https://api.lolicon.app/setu/v2?"
HEADER = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"
}

# setu
def getSetuInfo(keyword: str):
    if keyword[0]=='!':
        keyword = keyword[1:-2]
    else:
        keyword = keyword[2:-2]
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
        return None
    ans = '作者：' + author + '\n链接：' + urlmsg
    return [ans, js['data'][0]['urls']['original'].replace('cat', 're', 1)]


def pidGetCatUrl(pid):
    pass

def setuMesg(setu_url: str):
    # pic
    # imgurl = js['data'][0]['urls']['original'].replace('cat', 're', 1)
    # await session.send("[CQ:image,file=" + imgurl + ",cache=1]")
    # print(setu_url)
    return MessageSegment.image(setu_url, timeout=114514)
    

# saucenao

def getCQimgInMesg(mesg: str):
    mesg = ''.join(mesg.strip().split(' '))
    CQimg = re.findall('\[CQ:image[^\]]*', mesg)
    return CQimg

def getImgUrlInCQ(CQ: list):
    ans = []
    for mesg in CQ:
        url = mesg[mesg.find('url') + 4:]
        ans.append(url)
    return ans

def saucenaoSearch(urllist):
    pass