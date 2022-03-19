import asyncio
from nonebot import on_command, CommandSession
import random
import time

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
    res = await async_request(url=url, params=para)
    res = res.json()
    res = res[0]
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
    res = await async_request(url=OSUGETUSERRE, params=para)
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
    res = await async_request(url=OSUGETBEATMAP, params=para)
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