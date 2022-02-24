import httpx
from nonebot import on_command, CommandSession, MessageSegment
import requests
from random import choice
import re

SETUAPI = r"https://api.lolicon.app/setu/v2?"
HEADER = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"
}

# setu
async def getSetuInfo(keyword: str):
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
        async with httpx.AsyncClient() as client:
            res = await client.get(url=url)
        js = res.json()
        pid = str(js['data'][0]['pid'])
        uid = str(js['data'][0]['uid'])
        author = str(js['data'][0]['author'])
        urlmsg = "https://pixiv.net/i/" + pid
    except:
        return None
    ans = '作者：' + author + '\n链接：' + urlmsg
    return [ans, js['data'][0]['urls']['original'].replace('cat', 're', 1)]


def pidGetPixivurl(pid):
    '''
    用pixivid拼接URL
    '''
    if not pid:
        return None
    return "https://pixiv.net/i/" + str(pid)

def setuMesg(setu_url: str):
    '''
    传入图片url得到可以通过bot.send()发送的MessageSegment
    '''
    # pic
    # imgurl = js['data'][0]['urls']['original'].replace('cat', 're', 1)
    # await session.send("[CQ:image,file=" + imgurl + ",cache=1]")
    print(setu_url)
    return MessageSegment.image(setu_url)
    

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

def dealNone(dic: dict):
    for key, value in dic.items():
        if not value:
            dic[key] = 'None'
    return dic

async def saucenaoSearch(urllist: list, SAUCEURL: str):
    '''
    传入图片list及SAUCE已经拼接好参数的url进行图片检索
    返回图片检索得到的一些基本信息list
    index_id表：https://saucenao.com/tools/examples/api/index_details.txt
    可以查搜索得到的type，没写
    '''
    info = []
    for img in urllist:
        print("\n\n\n")
        try:
            print(SAUCEURL + img)
            async with httpx.AsyncClient() as client:
                data = await client.get(url= SAUCEURL + img)
            #data = requests.get(SAUCEURL + img, headers=HEADER).json()
            data = data.json()
            #print(data)
            #print(data["results"])
        except BaseException as e:
            print(e)
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
                tmp["url"] = data["data"].get("ext_urls")
                tmp["creator"] = data["data"].get('creator')
                tmp['title'] = data['data'].get('title')
                tmp['pixiv_url'] = pidGetPixivurl(data['data'].get('pixiv_id'))
                tmp["eng_name"] = data["data"].get('eng_name')
                tmp["jp_name"] = data["data"].get('jp_name')
                tmp["type"] = "pic"
                if tmp["eng_name"] or tmp["jp_name"]:
                    tmp["type"] = "doujin" 
                tmp = dealNone(tmp)
                info.append(tmp)
    #print("\n\n\n")
    #print(info)
    #print("\n\n\n")
    return info

        



