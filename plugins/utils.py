from tokenize import String
from nonebot import on_command, CommandSession, MessageSegment
import requests
from random import choice
from bs4 import BeautifulSoup
import re

from sklearn.feature_extraction import img_to_graph

URL = r"https://api.lolicon.app/setu/v2?"
HEADER = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"
}

# setu
def getSetuInfo(keyword: str):
    '''
    从消息中提取涩图tag并获取涩图的info
    '''
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
    '''
    传入图片url得到可以通过bot.send()发送的MessageSegment
    '''
    # pic
    # imgurl = js['data'][0]['urls']['original'].replace('cat', 're', 1)
    # await session.send("[CQ:image,file=" + imgurl + ",cache=1]")
    # print(setu_url)
    return MessageSegment.image(setu_url, timeout=114514)
    

# saucenao

def getCQimgInMesg(mesg: str):
    '''
    把原始消息中所有图片的CQ码分离出来

    返回CQ码的list
    '''
    mesg = ''.join(mesg.strip().split(' '))
    CQimg = re.findall('\[CQ:image[^\]]*', mesg)
    return CQimg

def getImgUrlInCQ(CQ: list):
    '''
        需要满足
        [CQ:image,
        file=xxxx,
        url=xxxx,subType=x]
        这种格式

        返回url=后面除去]的所有内容
    '''
    ans = []
    for mesg in CQ:
        url = mesg[mesg.find('url') + 4:]
        ans.append(url)
    return ans

def saucenaoSearch(urllist: list, SAUCEURL: str):
    '''
    传入图片list及SAUCE已经拼接好参数的url进行图片检索
    返回图片检索得到的一些基本信息list
    index_id表：https://saucenao.com/tools/examples/api/index_details.txt
    可以查搜索得到的type，没写
    '''
    info = []
    for img in urllist:
        #print("\n\n\n")
        try:
            data = requests.get(SAUCEURL + img, timeout=5).json()
            #print(data["results"])
        except:
            return None
        res = data.get("results", "result")

        for i in range(3):
            data = res[i]
            #print("\n\n\n")
            #print(data)
            similarity = data["header"]["similarity"]
            thumbnail = data["header"]["thumbnail"] # 缩略图 : url

            if float(similarity) >= 70:
                tmp = {}
                tmp["similarity"] = similarity
                tmp["thumbnail"] = thumbnail
                tmp["index_name"] = data["header"]["index_name"]
                tmp["url"] = choice(data["data"].get("ext_urls", ["None"]))
                tmp["creator"] = data["data"].get('creator')
                tmp["eng_name"] = data["data"].get('eng_name')
                tmp["jp_name"] = data["data"].get('jp_name')
                tmp["type"] = "pic"
                if tmp["eng_name"] or tmp["jp_name"]:
                    tmp["type"] = "doujin" 
                info.append(tmp)
    print("\n\n\n")
    print(info)
    print("\n\n\n")
    return info

        



