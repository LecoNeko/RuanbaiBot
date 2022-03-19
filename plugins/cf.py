import asyncio
from nonebot import on_command, CommandSession, Message
from plugins.utils import *


HEADER = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"
}

fk = '命令不合法'

LUOGUPROBLEM = 'https://www.luogu.com.cn/problem/'
CFINFOURL = r'https://codeforces.com/api/user.info?handles='
CFRATINGURL = r'https://codeforces.com/api/user.rating?handle='
CFSTATUS = r'https://codeforces.com/api/user.status?from=1&count={}&handle='
CFCONTESTS = r'https://codeforces.com/api/contest.list?gym=false'
OJHUNT = 'https://ojhunt.com/api/crawlers/'


luoguLimit = {'time': time.time(), 'cnt':0}
SwaggerLimit = {'time': time.time(), 'cnt':0}

def timeChecker():
    if time.time() - luoguLimit['time'] > 60:
        luoguLimit['time'] = time.time()
        luoguLimit['cnt'] = 0
    if luoguLimit['cnt'] > 30:
        return False
    luoguLimit['cnt'] += 1
    return True


@on_command(name='algorithm problem solved counter', patterns='来一?[点份].*[刷做过]题数?')
async def _(session: CommandSession):
    if time.time() - SwaggerLimit['time'] > 60:
        SwaggerLimit['time'] = time.time()
        SwaggerLimit['cnt'] = 0
    if SwaggerLimit['cnt'] >= 10:
        await session.send('请求过于频繁！请稍后再试试吧~')
        return
    SwaggerLimit['cnt'] += 5
    cur_text = session.current_arg_text.strip()
    cur_text = re.findall('[点份].*[刷做过]', cur_text)
    if not cur_text:
        await session.send('需要ID才能查询QAq')
    User = cur_text[0][1:-1]
    ans = await countOJTotalProblemSolve(User)
    await session.send(ans)



@on_command(name='cf', patterns=gene_Aa_ReStr('codeforces'), privileged = True, only_to_me=True)
async def _(session: CommandSession):
    cur_text = session.current_arg_text.strip().split()
    Method = cur_text[0]
    #print('\n\n\n')
    #print(Method)
    #print(User)
    if re.fullmatch(gene_Aa_ReStr('info'), Method):
        User = cur_text[1]
        Info = await CodeforcesInfo(User)
        if not Info or Info == '网络错误':
            await session.send(Info)
        ans = ''
        ans += Info['titlePhoto'] + '\n'
        ans += 'Name: ' + Info['name'] + '\n'
        if Info['country']:
            ans += 'Country: ' + Info['country'] + '\n'
        ans += 'Rating: ' + str(Info['rating']) + ' ' + Info['rank'] + '\n'
        ans += 'MAXRating: ' +  str(Info['maxRating']) + ' ' + Info['maxRank']
        await session.send(ans)
    elif re.fullmatch(gene_Aa_ReStr('rtcg'), Method):
        User = cur_text[1]
        cnt = 1
        if len(cur_text) > 3:
            await session.send(fk)
        if len(cur_text)== 3:
            cnt = int(cur_text[2])
        ans = await CodeforcesRating(User, cnt)
        await session.send(ans)
    elif re.fullmatch(gene_Aa_ReStr('lastsb'), Method):
        User = cur_text[1]
        ans = await CodeforcesLastSubmission(User)
        await session.send(ans)
    elif re.fullmatch(gene_Aa_ReStr('status'), Method):
        User = cur_text[1]
        ans = await CodeforcesStatus(User)
        await session.send(ans)
    elif re.fullmatch(gene_Aa_ReStr('rect'), Method):
        ans = await CodeforcesRecentContests()
        for item in ans:
            print(item)
            await session.send(item)
    elif re.fullmatch(gene_Aa_ReStr('pb'), Method):
        if timeChecker() == False:
            await session.send('请求过于频繁！请稍后再试试吧~')
            return
        name = str(cur_text[1])
        if name[0].isdigit():
            name = 'CF' + name
        name = name.upper()
        path = os.path.join(os.path.dirname(__file__), 'temp')
        path = os.path.join(path, 'luogu.png')
        getWebImage(LUOGUPROBLEM + name, path)
        path = path.replace('\\','/')
        await session.send(MessageLocalImage(path))



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
        print(item)
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
        temp = name + ' \n' + '比赛时长：' + str(durationSeconds) + 'mins\n'\
            + '日期：{}年{}月{}日{}时{}分  星期{}'.format(\
                year, month, day, hour, min, WEEKDAY[wday])
        ans.append(temp)
    #print(ans)
    return ans





async def getTotAndSub(url):
    tot = 0
    submissions = 0
    #print('\n\n\n')
    #print(url)
    try:
        res = await async_request(url)
    except:
        return [0,0]
    try:
        res = res.json()
        
        if str(res['error']) == 'True':
            return [0,0]
        print(res)
        res = res['data']
        tot += int(res['solved'])
        submissions += int(res['submissions'])
    except:
        return [0,0]
    return [tot, submissions]

async def itemGenerator(items:list, url:str):
    item = await getTotAndSub(url)
    items.append(item)

async def getOJList():
    try:
        res = await async_request(OJHUNT)
        res = res.json()
    except:
        return '网络错误'
    
    if str(res['error']) == 'true':
        return '查询失败QAq'
    res = res['data']
    ojname = []
    # print(res)
    for k, v in res.items():
        ojname.append(str(k))
    return ojname
ojname = ['poj', 'codeforces', 'vjudge', 'luogu', 'atcoder']
async def countOJTotalProblemSolve(User):
    
    #ojname = await getOJList()
    #print('\n\n\n')
    #for i in ojname:
    #    print(i)
    tot = 0
    submissions = 0
    items = []
    funct = []
    for name in ojname:
        url = OJHUNT + name + '/' + User
        funct.append(itemGenerator(items, url))
    await asyncio.gather(*funct)
    print(items)
    for item in items:
        tot += item[0]
        submissions += item[1]

    ans = '当前仅返回poj, codeforces, vjudge, luogu, atcoder的提交统计\n\n'
    ans += 'ID：' + User + '\n'
    ans += 'AC总数：' + str(tot) + '(可能包含重复的remotejudge)\n'
    ans += '提交次数：' + str(submissions)
    return ans


