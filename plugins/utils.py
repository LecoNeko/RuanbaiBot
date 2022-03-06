from time import localtime
import httpx
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from nonebot import on_command, CommandSession, MessageSegment
import requests
import re
import time
from io import BytesIO
import os
from PIL import Image

from config import OSU_API_KEY

SETUAPI = r"https://api.lolicon.app/setu/v2?"
HEADER = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"
}


def getWebImage(url:str, pic_path:str):
    '''
    抓取网站全屏截图
    '''
#chromedriver的路径
    chromedriver = r"C:\Program Files\Google\Chrome\Application\chromedriver.exe"
    os.environ["webdriver.chrome.driver"] = chromedriver
#设置chrome开启的模式，headless就是无界面模式
#一定要使用这个模式，不然截不了全页面，只能截到你电脑的高度
    chrome_options = Options()
    chrome_options.add_argument('headless')
    driver = webdriver.Chrome(chromedriver,chrome_options=chrome_options)
#控制浏览器写入并转到链接
    driver.get(url)
    time.sleep(1)
#接下来是全屏的关键，用js获取页面的宽高，如果有其他需要用js的部分也可以用这个方法
    width = driver.execute_script("return document.documentElement.scrollWidth")
    height = driver.execute_script("return document.documentElement.scrollHeight")
    print(width,height)
#将浏览器的宽高设置成刚刚获取的宽高
    driver.set_window_size(width, height)
    time.sleep(1)
#截图并关掉浏览器
    driver.save_screenshot(pic_path)
    driver.close()


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
    path = path.replace('\\','/')
    # path.replace('\\','/')
    return '[CQ:image,file=file:///' + path + ']'

def pathRenameByRange(path: str):
    filenames = os.listdir(path)
    siz = len(filenames)
    for i in range(siz):
        file = os.path.join(path, filenames[i])
        filename, filetype = os.path.splitext(file)
        os.rename(file, os.path.join(path,str(i))+str(filetype))



# setu
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
    print(url)
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



# Osu

OSUAPIURL = 'https://osu.ppy.sh/api/'

async def OsuInfo(User: str, mode: str):
    if mode != '3':
        return '当前只支持查询osu!mania模式QAQ'
    url = OSUAPIURL + 'get_user'
    para = {}
    para['k'] = OSU_API_KEY
    para['u'] = User
    para['m'] = mode
    para['type'] = 'string'
    res = requests.get(url=url, params=para)
    res = res.json()
    res = res[0]
    #print('\n\n\n')
    #print(res)
    user_id = str(res['user_id'])
    username = res['username']
    playcount = res['playcount']
    pp_raw = res['pp_raw']
    country = res['country']
    total_hours_played = round(float(res['total_seconds_played']) / 3600.0, 1)
    pp_rank = res['pp_rank']
    pp_country_rank = res['pp_country_rank']
    titleimgurl = 'http://s.ppy.sh/a/' + user_id
    img = imgsrcToPILobj(titleimgurl)
    thumbnail_path = makeThumbnail(img, 150, 'osuTitlephoto.jpg')
    titlethum = MessageLocalImage(thumbnail_path)
    ans = titlethum + '\n'
    ans += username + '\n'
    ans += 'pp: ' + str(pp_raw) + '  排名:' + str(pp_rank) + '\n'
    ans += '国家: ' + country +'  国内排名: ' + str(pp_country_rank) + '\n'
    ans += '游戏次数: ' + str(playcount) + '  总时长: ' + str(total_hours_played) + '时'
    return ans

BEATMAPIMG = 'https://assets.ppy.sh/beatmaps/{}/covers/cover.jpg'
OSUGETUSERRE = 'https://osu.ppy.sh/api/get_user_recent'
OSUGETBEATMAP = 'https://osu.ppy.sh/api/get_beatmaps'
accRate = [100/6,100/3,100/3*2,100,100,0]


def getAcc(cnt:list):
    tot = 0
    iter = 0
    while iter < 6:
        tot += int(cnt[iter])
        iter += 1
    iter = 0
    ans = 0
    while iter < 6:
        ans += float(cnt[iter]) / tot * accRate[iter]
        iter += 1
    return ans
    
async def OsuRe(User: str, mode: int):
    if mode != '3':
        return '当前只支持查询osu!mania模式QAQ'
    para = {}
    para['k'] = OSU_API_KEY
    para['u'] = User
    para['m'] = mode
    res = requests.get(url=OSUGETUSERRE, params=para)
    res = res.json()
    res = res[0]
    score = res['score']
    beatmap_id = res['beatmap_id']
    maxcombo = res['maxcombo']
    miss = res['countmiss']
    cnt50 = res['count50']
    cnt100 = res['count100']
    cnt200 = res['countkatu']
    cnt300 = res['count300']
    cntrgb = res['countgeki']
    acc = getAcc([cnt50,cnt100,cnt200,cnt300,cntrgb,miss])
    rank = res['rank']
    date = res['date']
    date = time.localtime(time.mktime(time.strptime(date, '%Y-%m-%d %H:%M:%S')) + 3600 * 8)
    date = time.strftime("%Y-%m-%d %H:%M:%S", date)
    para.clear()
    para['k'] = OSU_API_KEY
    para['b'] = beatmap_id
    res = requests.get(url=OSUGETBEATMAP, params=para)
    res = res.json()
    res = res[0]
    beatmapset_id = res['beatmapset_id']
    img = BEATMAPIMG.format(beatmapset_id)
    img = imgsrcToPILobj(img)
    thumbnail_path = makeThumbnail(img, 400, 'osuTitlephoto.jpg')
    titlethum = MessageLocalImage(thumbnail_path)
    title = res['title']
    BPM = res['bpm']
    stars = res['difficultyrating']
    ans = titlethum + '\n图名：{}  BPM：{}  难度:{}stars'.format(title, BPM, round(float(stars),2)) + '\n'
    ans += 'score：{} maxcombo：{}\n彩300：{} 黄300：{}\n200：{}\n100：{}\n50：{}\n'.format(\
        score, maxcombo, cntrgb, cnt300, cnt200, cnt100, cnt50)
    ans += '黄彩：{} ACC：{}% RANK：{}\n'.format(round(float(cntrgb)/float(cnt300), 1), round(acc, 2), rank)
    ans += "时间：{}".format(date)
    # print(ans)
    return ans

