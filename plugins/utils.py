from time import localtime
import httpx
import json
from nonebot import on_command, CommandSession, MessageSegment
import requests
import re
from io import BytesIO
import os
from PIL import Image

SETUAPI = r"https://api.lolicon.app/setu/v2?"
HEADER = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"
}

async def async_request(url):
    async with httpx.AsyncClient() as client:
        res = await client.get(url)
    return res

def rmsgToJson(msg: str)->dict:
    if not msg:
        return None
    msg = msg[msg.find('data')+5:]
    i = len(msg)-1
    j = 0
    while msg[i]!= '}':
        i-=1
        j-=1
    msg = msg[:j]
    msg = re.sub('&#44;', ',', msg)
    msg = re.sub(';', ',', msg)
    #print('\n\n\n')
    #print(msg)
    #print('\n\n\n\n\n')
    return json.loads(msg)


def gene_Aa_ReStr(String:str):
    res = ''
    for i in String:
        #print(type(i))
        res = res +'['+ i.lower() + i.upper() + ']'
    return res

def imgsrcToPILobj(imgsrc):
    imgres = requests.get(imgsrc)
    img = Image.open(BytesIO(imgres.content))
    return img

def makeThumbnail(img: Image, base_width, filename):
    '''
    等比例缩放图片
    '''
    height = int(img.size[1] * base_width / float(img.size[0]))
    thumbnail = img.resize((base_width, height), Image.ANTIALIAS)
    thumbnail_path = os.path.join(os.path.dirname(__file__),'temp')
    thumbnail_path = os.path.join(thumbnail_path, filename)
    thumbnail.save(thumbnail_path)
    return thumbnail_path.replace('\\','/')

def MessageLocalImage(path:str):
    '''
    转换为本地文件传输协议的CQ码
    '''
    # path.replace('\\','/')
    return '[CQ:image,file=file:///' + path + ']'




# setu
async def getSetuInfo(keyword: str, R18flag: int):
    '''
    从消息中提取涩图tag并获取涩图的info
    '''
    if keyword=='炼铜' or keyword=='重工业':
        url = SETUAPI + 'tag=萝莉|幼女'
    else:
        keyword = keyword[2:-2]
        tmp = re.sub('[Rr]18', '', keyword)
        r18 = R18flag

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
    #print('\n')
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
            data = await async_request(url= SAUCEURL + img)
            #data = requests.get(SAUCEURL + img, headers=HEADER).json()
            data = data.json()
            #print(data)
            #print(data["results"])
        except BaseException as e:
            print(e)
            return None
        res = data.get("results", "result")
        first_search_res = 0
        for i in range(3):
            data = res[i]
            #print("\n\n\n")
            #print(data)
            similarity = data["header"]["similarity"]
            thumbnail = data["header"]["thumbnail"] # 缩略图 : url

            if float(similarity) >= 70 or first_search_res == 0:
                first_search_res = 1
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





# Codeforces

CFINFOURL = r'https://codeforces.com/api/user.info?handles='
CFRATINGURL = r'https://codeforces.com/api/user.rating?handle='
CFSTATUS = r'https://codeforces.com/api/user.status?from=1&count={}&handle='
CFCONTESTS = r'https://codeforces.com/api/contest.list?gym=false'

async def CodeforcesInfo(User:str):
    res = await async_request(CFINFOURL + User)
    res = res.json()
    if not res or res['status']!='OK':
        return '查询失败QAQ'
    res = res['result'][0]
    cfInfo = {}
    cfInfo['name'] = res.get('handle', None)
    cfInfo['country'] = res.get('country', None)
    cfInfo['city'] = res.get('city', None)
    cfInfo['rating'] = res.get('rating', None)
    cfInfo['rank'] = res.get('rank', None)
    cfInfo['maxRating'] = res.get('maxRating', None)
    cfInfo['maxRank'] = res.get('maxRank', None)

    # 头像缩略图
    imgsrc = res['titlePhoto']
    img = imgsrcToPILobj(imgsrc)
    thumbnail_path = makeThumbnail(img, 50, 'cfTitlephoto.jpg')
    cfInfo['titlePhoto'] = MessageLocalImage(thumbnail_path)
    return cfInfo

async def CodeforcesRating(User:str, cnt:int):
    res = await async_request(CFRATINGURL + User)
    res = res.json()
    if not res or res['status']!='OK':
        return '查询失败QAQ'
    res = res['result']
    res = sorted(res, key = lambda x : x['contestId'], reverse=True)
    now = min(len(res), cnt) - 1
    ans = '最近' + str(now+1) + '场的'
    totalchange = res[0]['newRating'] - res[now]['oldRating']
    
    ans += '总rating变化: ' + str(totalchange) + '\n' + '上分的场次'
    if now > 4:
        ans += '(取最近5场中的)'
    ans += ': \n'
    now = min(4, now)
    banzhuan = 1
    while now >= 0:
        if res[now]['newRating'] - res[now]['oldRating'] > 0:
            banzhuan = 0
            ans += res[now]['contestName'] + ' ' +\
                 str(res[now]['oldRating']) + ' -> ' + str(res[now]['newRating'])
            if now != 0:
                ans += '\n'
        now -= 1
    if banzhuan == 1:
        if len(res) >= 5:
            ans += '打ACM也就图一乐，早点找个电子厂上班吧'
        else:
            ans += 'return 下分'
    return ans

async def CodeforcesLastSubmission(User: str):
    res = await async_request(CFSTATUS.format('1') + User)
    res = res.json()
    if not res or res['status']!='OK':
        return '查询失败QAQ'
    res = res['result'][0]
    name = res['problem']['index'] + '——'+ res['problem']['name']
    score = res['problem'].get('rating', 0)
    tag = str(res['problem']['tags'])
    Language = res['programmingLanguage']
    verdict = res['verdict'].replace('OK', 'ACCEPT')
    ans = '上次提交的题目是：'+ name +'(rating = ' + str(score) + ')\n'
    ans += '语言：' + Language + '\n'
    ans += '结果：' + verdict
    return ans

async def CodeforcesStatus(User: str):
    res = await async_request(CFSTATUS.format('5') + User)
    res = res.json()
    if not res or res['status']!='OK':
        return '查询失败QAQ'
    Res = res['result']
    ed = min(5, len(Res))
    ans = ''
    for i in range(ed):
        res = Res[i]
        name = res['problem']['index'] + '——'+ res['problem']['name']
        score = res['problem'].get('rating', 0)
        #tag = str(res['problem']['tags'])
        #Language = res['programmingLanguage']
        verdict = res['verdict'].replace('OK', 'ACCEPT')
        ans += name +'(rating = ' + str(score) + ')\n'
        ans += '结果：' + verdict
        if i != ed - 1:
            ans += '\n'
    return ans


WEEKDAY = ' 一二三四五六日'

async def CodeforcesRecentContests():
    res = await async_request(CFCONTESTS)
    res = res.json()
    if not res or res['status']!='OK':
        return '查询失败QAQ'
    res = res['result']
    ans = ['最近未开始的比赛有：\n']
    
    for item in res:
        if item.get('phase')=='FINISHED':
            break
        name = item['name']
        durationSeconds = float(item['durationSeconds']) / 60.0
        startTime = localtime(item['startTimeSeconds'])
        year = startTime[0]
        month = startTime[1]
        day = startTime[2]
        hour = startTime[3]
        min = startTime[4]
        wday = startTime[6]
        temp = name + '\n' + '比赛时长：' + str(durationSeconds) + 'mins\n'\
            + '日期：{}年{}月{}日{}时{}分  星期{}'.format(\
                year, month, day, hour, min, WEEKDAY[wday])
        ans.append(temp)
    return ans
        